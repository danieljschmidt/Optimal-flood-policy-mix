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
# same population; with SFHA_ONLY = False the sample covers all flood zones and no longer mirrors it.  Caveats that cannot be fixed in the data pipeline — the denominator
# is building value, not wealth, and the sample is conditional on a claim being filed,
# not on a flood occurring — are documented in notes/notes.md.
# The *_home variants rescale each claim by (1 - FHFA land share) to express damage as a
# share of home value including land (the denominator the macro model uses).
# Companion to run_compute_damage_grid3.py (3-point grids, depth-damage fit, 2100 projection).

from pathlib import Path

import numpy as np
import pandas as pd
import matplotlib.pyplot as plt
import sqlite3

from discretize_damage import discretize_conditional_means

# %% Configuration

DATA_DIR = Path(r"C:\Users\TPRINS\OneDrive - UvA\Documenten\Python files insurance-aid\Code August 2026\fema_data_analysis\data")
DB_PATH = DATA_DIR / "fema.db"
LAND_PATH = DATA_DIR / "land-prices_2024_20_june.xlsx"   # FHFA WP 19-01 land prices, v4.0

SFHA_ONLY = True       # True: SFHA claims only (zones A*, V*); False: claims in all flood zones
SAMPLE = "SFHA" if SFHA_ONLY else "all-zone"
ZONE_FILTER = ("AND (UPPER(TRIM(ratedFloodZone)) LIKE 'A%' OR UPPER(TRIM(ratedFloodZone)) LIKE 'V%')"
               if SFHA_ONLY else "")

N_BINS = 20            # bin width 0.05 on [0, 1]
MIN_YEAR = 2000        # see notes: pre-2000 property values are badly contaminated
VALUE_MIN = 10_000     # plausibility band on the denominator
VALUE_MAX = 10_000_000
MAX_RATIO = 1.5        # damage/value above this is treated as a data error and dropped;
                       # ratios in (1, MAX_RATIO] are clipped to 1 (total loss)

OUT_DIR = Path(__file__).resolve().parent / "output"
if not SFHA_ONLY:
    OUT_DIR = OUT_DIR / "all_zones"   # SFHA outputs stay where downstream code expects them
OUT_DIR.mkdir(parents=True, exist_ok=True)

# %% Connect to database

conn = sqlite3.connect(DB_PATH)

# %% Load claims data
#
# Pulled once as a superset (single-family + SFHA, all years);
# every sample variant below is carved out of this frame in pandas.

df_claims = pd.read_sql_query(
    f"""
    SELECT
        ratedFloodZone,
        yearOfLoss,
        floodEvent,
        buildingDamageAmount,
        buildingPropertyValue,
        elevatedBuildingIndicator,
        postFIRMConstructionIndicator,
        buildingReplacementCost,
        replacementCostBasis,
        censusGeoid,
        reportedZipCode,
        countyCode,
        state
    FROM claims
    WHERE
        occupancyType IN (1, 11) AND
        buildingDamageAmount IS NOT NULL AND
        buildingPropertyValue IS NOT NULL
        {ZONE_FILTER}
    """,
    conn
)

print(f"claims loaded (single-family, {SAMPLE}, damage and value reported): {len(df_claims):,}")
in_sfha = df_claims["ratedFloodZone"].astype("string").str.strip().str.upper().str[0].isin(["A", "V"])
print(f"  share of these claims in an SFHA (A, V): {in_sfha.mean():.1%}")

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

# Diagnostic: damage above building value.  Both amounts are actual cash value, so a
# ratio > 1 should not occur.  If these claims mostly have damage <= replacement cost and
# a replacement-cost settlement basis, damage was probably recorded at replacement cost,
# and damage / buildingReplacementCost would be the better ratio than clipping to 1.

r = df_claims["fracDamage"]
above = r > 1
in_band = above & (r <= MAX_RATIO)
rc = df_claims["buildingReplacementCost"].astype("float64")
frac_rc = df_claims["buildingDamageAmount"] / rc.where(rc > 0)

print(f"\n  ratio > 1: {int(above.sum()):,} claims ({above.mean():.2%}); quantiles of the ratio among them:")
print(r[above].quantile([0.25, 0.5, 0.75, 0.9, 0.99]).round(3).to_string())
print(f"  ratio in (1, {MAX_RATIO}]: {int(in_band.sum()):,}; replacement cost reported: "
      f"{int(frac_rc[in_band].notna().sum()):,}; damage <= replacement cost: {int((frac_rc[in_band] <= 1).sum()):,}")
print("  replacementCostBasis, share within group:")
print(pd.crosstab(df_claims["replacementCostBasis"].astype("string").fillna("missing"),
                  np.where(above, "ratio > 1", "ratio <= 1"), normalize="columns").round(3).to_string())
print()

n_too_high = int((df_claims["fracDamage"] > MAX_RATIO).sum())
df_claims = df_claims[df_claims["fracDamage"] <= MAX_RATIO].copy()

n_above_one = int((df_claims["fracDamage"] > 1).sum())
df_claims["fracDamage"] = df_claims["fracDamage"].clip(0, 1)

print(f"  dropped, denominator == 0                  : {n_zero_value:,}")
print(f"  dropped, denominator outside plausible band: {n_out_of_band:,}")
print(f"  dropped, ratio non-finite                  : {n_nonfinite:,}")
print(f"  dropped, ratio > {MAX_RATIO} (data error)         : {n_too_high:,}")
print(f"  clipped, ratio in (1, {MAX_RATIO}] -> 1           : {n_above_one:,}")

# %% Land share and damage as a share of home value (structure + land)
#
# FHFA pooled 2012-2022 land share of single-family property value (Davis, Larson,
# Oliner & Shui; FHFA WP 19-01).  Land is not destroyed, so
#     damage / home value = damage / structure value * (1 - land share).
# Matched at the finest level available: tract -> ZIP -> county -> state.

def load_land_shares(path):
    sheets = {s.strip(): s for s in pd.ExcelFile(path).sheet_names}   # 'Cross-Section Counties ' has a trailing space

    def read(sheet, id_col, width):
        d = pd.read_excel(path, sheet_name=sheets[sheet], header=1)
        ids = d[id_col].astype(str).str.strip()
        if width:
            ids = d[id_col].astype("int64").astype(str).str.zfill(width)   # restore leading zeros
        return pd.Series(d["Land Share of Property Value"].to_numpy(), index=ids)

    return {
        "tract":  read("Cross-Section Census Tracts", "Census Tract", 11),
        "zip":    read("Cross-Section ZIP Codes", "ZIP Code", 5),
        "county": read("Cross-Section Counties", "FIPS", 5),
        "state":  read("Cross-Section States", "State Abbreviation", None),
    }

land = load_land_shares(LAND_PATH)

county = df_claims["countyCode"].astype("string").str.strip().str.zfill(5)
tract = df_claims["censusGeoid"].astype("string").str.strip().str[:11]
tract = tract.where((tract.str[:5] == county).fillna(False))   # geoid must sit inside the claim's county
keys = {
    "tract":  tract,
    "zip":    df_claims["reportedZipCode"].astype("string").str.strip().str[:5].str.zfill(5),
    "county": county,
    "state":  df_claims["state"].astype("string").str.strip(),
}

df_claims["landShare"] = np.nan
df_claims["landShareLevel"] = "unmatched"
for level, key in keys.items():
    todo = df_claims["landShare"].isna()
    df_claims.loc[todo, "landShare"] = key[todo].map(land[level]).astype("float64")
    df_claims.loc[todo & df_claims["landShare"].notna(), "landShareLevel"] = level

df_claims["fracDamageHome"] = df_claims["fracDamage"] * (1 - df_claims["landShare"])

matched = df_claims["landShare"].notna()
print("\nland share matched at level (share of claims):")
print(df_claims["landShareLevel"].value_counts(normalize=True).round(4).to_string())
print(f"  mean land share (matched claims): {df_claims['landShare'].mean():.3f}")
print(f"  mean damage/structure, all vs matched claims: "
      f"{df_claims['fracDamage'].mean():.4f} vs {df_claims.loc[matched, 'fracDamage'].mean():.4f}")

# %% Sample variants
#
# main            -- the baseline
# excl_katrina    -- Katrina alone is 12% of the main sample and carries most of the upper tail
# since_2010      -- post-Katrina window: cleaner reporting, current building stock

modern = df_claims["yearOfLoss"] >= MIN_YEAR
katrina = df_claims["floodEvent"] == "Hurricane Katrina"

VARIANTS = {
    "main": (
        f"single-family {SAMPLE} claims from {MIN_YEAR} onward",
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
    # same samples, damage as a share of home value (claims without a land share drop out)
    "main_home": (
        "main sample, damage / home value incl. land",
        modern, "fracDamageHome",
    ),
    "excl_katrina_home": (
        "main sample excluding Hurricane Katrina, damage / home value incl. land",
        modern & ~katrina, "fracDamageHome",
    ),
    "since_2010_home": (
        "2010 onward, damage / home value incl. land",
        df_claims["yearOfLoss"] >= 2010, "fracDamageHome",
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

# Same tables as one Excel workbook (CSV columns merge in Excel with a Dutch locale)
with pd.ExcelWriter(OUT_DIR / "damage_distribution.xlsx") as xl:
    df_summary.to_excel(xl, sheet_name="summary", index=False)
    for name, table in distributions.items():
        table.to_excel(xl, sheet_name=name, index=False)

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
COLORS = ["#184f95", "#eb6834", "#86b6ef", "#4a9c6d", "#898781", "#b8860b"]

for (name, table), color in zip(distributions.items(), COLORS):
    centres = 0.5 * (table["damage_ratio_lower"] + table["damage_ratio_upper"])
    row = df_summary.set_index("variant").loc[name]
    ax.plot(centres, table["weight"], marker="o", markersize=4, linewidth=2, color=color,
            label=f"{name} (mean {row['mean']:.3f}, CV {row['cv']:.3f})")

ax.set_xlabel("Damage / building value (*_home: / home value incl. land)")
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