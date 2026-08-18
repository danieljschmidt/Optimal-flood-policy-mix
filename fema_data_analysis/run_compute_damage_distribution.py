# %%
# Compute the empirical flood-damage distribution from OpenFEMA NFIP claims.
#
# Object produced: the distribution of  buildingDamageAmount / buildingPropertyValue
# ("share of building value destroyed"), discretized into equal-width bins represented
# by their conditional means.  One CSV and one histogram per sample variant, written to
# fema_data_analysis/output/.
#
# The sample definition mirrors fema_data_analysis/adaptation_analysis/run_adaptation_analysis.py
# (single-family residential, SFHA) so the damage and adaptation evidence describe the
# same population.  Caveats that cannot be fixed in the data pipeline — the denominator
# is building value, not wealth, and the sample is conditional on a claim being filed,
# not on a flood occurring — are documented in notes/notes.md.

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

from discretize_damage import discretize_conditional_means

# %% Configuration

DB_PATH = "C:\\Users\\dschm\\Documents\\Data\\FEMA\\fema.db"

N_BINS = 20            # bin width 0.05 on [0, 1]
MIN_YEAR = 2000        # see notes: pre-2000 property values are badly contaminated
VALUE_MIN = 10_000     # plausibility band on the denominator
VALUE_MAX = 10_000_000

OUT_DIR = Path(__file__).resolve().parent / "output"
OUT_DIR.mkdir(exist_ok=True)

# %% Connect to database

conn = sqlite3.connect(DB_PATH)

# %% Load claims data
#
# Pulled once as a superset (single-family + SFHA, all years);
# every sample variant below is carved out of this frame in pandas.

df_claims = pd.read_sql_query(
    """
    SELECT
        yearOfLoss,
        floodEvent,
        buildingDamageAmount,
        buildingPropertyValue,
        elevatedBuildingIndicator,
        postFIRMConstructionIndicator
    FROM claims
    WHERE
        occupancyType IN (1, 11) AND
        buildingDamageAmount IS NOT NULL AND
        buildingPropertyValue IS NOT NULL AND
        (UPPER(TRIM(ratedFloodZone)) LIKE 'A%' OR UPPER(TRIM(ratedFloodZone)) LIKE 'V%')
    """,
    conn
)

print(f"claims loaded (single-family, SFHA, damage and value reported): {len(df_claims):,}")

# %% Damage ratio
#
# Guard the denominator explicitly.  buildingPropertyValue == 0 with positive damage
# yields inf, which clip(0, 1) would silently turn into a total loss; 0/0 yields NaN,
# which the discretizer would silently drop.  Both are recorded, not absorbed.

n_zero_value = int((df_claims["buildingPropertyValue"] <= 0).sum())
n_out_of_band = int((~df_claims["buildingPropertyValue"].between(VALUE_MIN, VALUE_MAX)).sum()) - n_zero_value

df_claims = df_claims[df_claims["buildingPropertyValue"].between(VALUE_MIN, VALUE_MAX)].copy()
df_claims["fracDamage"] = df_claims["buildingDamageAmount"] / df_claims["buildingPropertyValue"]

n_nonfinite = int((~np.isfinite(df_claims["fracDamage"])).sum())
df_claims = df_claims[np.isfinite(df_claims["fracDamage"])].copy()

n_above_one = int((df_claims["fracDamage"] > 1).sum())
df_claims["fracDamage"] = df_claims["fracDamage"].clip(0, 1)

print(f"  dropped, denominator == 0                  : {n_zero_value:,}")
print(f"  dropped, denominator outside plausible band: {n_out_of_band:,}")
print(f"  dropped, ratio non-finite                  : {n_nonfinite:,}")
print(f"  clipped, ratio > 1 (damage above value)    : {n_above_one:,}")

# %% Sample variants
#
# main            -- the baseline
# excl_katrina    -- Katrina alone is 12% of the main sample and carries most of the upper tail
# since_2010      -- post-Katrina window: cleaner reporting, current building stock

modern = df_claims["yearOfLoss"] >= MIN_YEAR
katrina = df_claims["floodEvent"] == "Hurricane Katrina"

VARIANTS = {
    "main": (
        f"single-family SFHA claims from {MIN_YEAR} onward",
        modern, "fracDamage",
    ),
    "excl_katrina": (
        "main sample excluding Hurricane Katrina",
        modern & ~katrina, "fracDamage",
    ),
    "since_2010": (
        "main sample restricted to 2010 onward",
        df_claims["yearOfLoss"] >= 2010, "fracDamage",
    ),
}

# %% Discretize each variant, write CSV + histogram

bin_edges = np.linspace(0, 1, N_BINS + 1)
summary_rows = []
distributions = {}

for name, (description, selection, column) in VARIANTS.items():
    x = df_claims.loc[selection, column].dropna().to_numpy()
    if len(x) == 0:
        raise ValueError(f"variant '{name}' selected no claims — check the filters")
    values, weights = discretize_conditional_means(x, N_BINS, [0, 1])

    counts = np.histogram(x, bins=bin_edges)[0]

    table = pd.DataFrame({
        "damage_ratio_lower": bin_edges[:-1],
        "damage_ratio_upper": bin_edges[1:],
        "damage_ratio_mean": values,     # conditional mean: the value the model should use
        "weight": weights,
        "n_claims": counts,
    })
    table.to_csv(OUT_DIR / f"damage_distribution_{name}.csv", index=False,
                 float_format="%.6f")
    distributions[name] = table

    mean_d = float(np.sum(values * weights))
    sd_d = float(np.sqrt(np.sum(weights * (values - mean_d) ** 2)))
    summary_rows.append({
        "variant": name,
        "description": description,
        "n_claims": len(x),
        "mean": x.mean(),
        "sd": x.std(),
        "cv": x.std() / x.mean(),
        "median": np.median(x),
        "share_zero": (x == 0).mean(),
        "share_above_0.9": (x >= 0.9).mean(),
        "mean_discretized": mean_d,
        "cv_discretized": sd_d / mean_d,
    })

df_summary = pd.DataFrame(summary_rows)
df_summary.to_csv(OUT_DIR / "damage_distribution_summary.csv", index=False, float_format="%.4f")

print("\nSample variants (mean and CV are the two calibration targets):")
print(df_summary.drop(columns=["description"]).round(4).to_string(index=False))

print("\nMain distribution:")
print(distributions["main"].round(4).to_string(index=False))

# %% Histogram of the main specification

x_main = df_claims.loc[VARIANTS["main"][1], "fracDamage"].to_numpy()

fig, ax = plt.subplots(figsize=(9, 4))
ax.hist(x_main, bins=50, density=True, color="#184f95")
ax.set_title(f"Damage / building value — {VARIANTS['main'][0]}\n"
             f"n = {len(x_main):,}   mean = {x_main.mean():.3f}   "
             f"CV = {x_main.std()/x_main.mean():.3f}", fontsize=10)
ax.set_xlabel("Damage / building value")
ax.set_ylabel("Density")
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
fig.tight_layout()
fig.savefig(OUT_DIR / "damage_distribution_main.png", dpi=200)
plt.show()

# %% Robustness: all variants in one line chart

fig, ax = plt.subplots(figsize=(9, 5))
COLORS = ["#184f95", "#eb6834", "#86b6ef", "#4a9c6d", "#898781"]

for (name, table), color in zip(distributions.items(), COLORS):
    centres = 0.5 * (table["damage_ratio_lower"] + table["damage_ratio_upper"])
    row = df_summary.set_index("variant").loc[name]
    ax.plot(centres, table["weight"], marker="o", markersize=4, linewidth=2, color=color,
            label=f"{name} (mean {row['mean']:.3f}, CV {row['cv']:.3f})")

ax.set_xlabel("Damage / building value")
ax.set_ylabel("Weight")
ax.set_title("Discretized damage distribution by sample variant")
ax.grid(True, color="#e1e0d9", linewidth=0.8)
ax.set_axisbelow(True)
ax.spines[["top", "right"]].set_visible(False)
ax.legend(frameon=False, fontsize=9)

fig.tight_layout()
fig.savefig(OUT_DIR / "damage_distribution_comparison.png", dpi=200)
plt.show()

print(f"\nwrote {len(VARIANTS)} distributions + summary + 2 figures to {OUT_DIR}")

# %%
