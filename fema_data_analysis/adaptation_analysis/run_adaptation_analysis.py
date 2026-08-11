# %% Import packages

import pandas as pd
import sqlite3
from pathlib import Path

# %% Connect to database

db_name = "C:\\Users\\dschm\\Documents\\Data\\FEMA\\fema.db"

conn = sqlite3.connect(db_name)

figures_dir = Path(__file__).parent / "figures"
figures_dir.mkdir(exist_ok=True)

tables_dir = Path(__file__).parent / "tables"
tables_dir.mkdir(exist_ok=True)

# %% 1. Elevated building rate by flood zone

df = pd.read_sql_query("""
    SELECT
        CASE
            WHEN (UPPER(TRIM(ratedFloodZone)) LIKE 'A%' OR UPPER(TRIM(ratedFloodZone)) LIKE 'V%') AND postFIRMConstructionIndicator = 1 THEN 'SFHA post-FIRM'
            WHEN (UPPER(TRIM(ratedFloodZone)) LIKE 'A%' OR UPPER(TRIM(ratedFloodZone)) LIKE 'V%') AND postFIRMConstructionIndicator = 0 THEN 'SFHA pre-FIRM'
            WHEN UPPER(TRIM(ratedFloodZone)) IN ('B', 'C', 'D', 'X') THEN 'non-SFHA'
            ELSE NULL
        END AS floodZoneCategory,
        strftime('%Y', policyEffectiveDate) AS policyYear,
        COUNT(*)                                   AS n_policies,
        AVG(CASE WHEN elevatedBuildingIndicator = 1 THEN 1.0 WHEN elevatedBuildingIndicator = 0 THEN 0.0 ELSE NULL END) AS pct_elevated,
        SUM(policyCost) * 1.0 / SUM(totalBuildingInsuranceCoverage) AS price_per_dollar_coverage
    FROM policies_sample
    WHERE ratedFloodZone IS NOT NULL
        AND occupancyType IN (1, 11) -- Only single-family residential buildings
        AND strftime('%Y', policyEffectiveDate) <= '2024'
    GROUP BY floodZoneCategory, policyYear
    HAVING floodZoneCategory IS NOT NULL
    ORDER BY policyYear, n_policies DESC;
    """,
    conn
)

print(df)
df.to_csv(tables_dir / "adaptation_by_flood_zone_over_time.csv", index=False)

# %% 2. Adaptation by rated flood zone and post-FIRM construction (2024 cross section)

df_2024 = pd.read_sql_query("""
    SELECT
        CASE
            WHEN UPPER(TRIM(ratedFloodZone)) LIKE 'A%' THEN 'SFHA A'
            WHEN UPPER(TRIM(ratedFloodZone)) LIKE 'V%' THEN 'SFHA V'
            WHEN UPPER(TRIM(ratedFloodZone)) IN ('B', 'C', 'D', 'X') THEN 'non-SFHA'
            ELSE UPPER(TRIM(ratedFloodZone))
        END AS floodZoneCategory,
        postFIRMConstructionIndicator,
        COUNT(*)                                              AS n_policies,
        AVG(CASE WHEN elevatedBuildingIndicator = 1 THEN 1.0 WHEN elevatedBuildingIndicator = 0 THEN 0.0 ELSE NULL END) AS pct_elevated,
        SUM(policyCost) * 1.0 / SUM(totalBuildingInsuranceCoverage) AS price_per_dollar_coverage
    FROM policies_sample
    WHERE ratedFloodZone IS NOT NULL
        AND occupancyType IN (1, 11) -- Only single-family residential buildings
        AND strftime('%Y', policyEffectiveDate) = '2024'
    GROUP BY floodZoneCategory, postFIRMConstructionIndicator
    ORDER BY floodZoneCategory, postFIRMConstructionIndicator;
    """,
    conn
)

print(df_2024)
df_2024.to_csv(tables_dir / "adaptation_by_flood_zone_2024_cross_section.csv", index=False)

# %% 3. Plot pct_elevated over time by flood zone category

import matplotlib.pyplot as plt

CATEGORICAL_COLORS = {
    "SFHA pre-FIRM": "#86b6ef",
    "SFHA post-FIRM": "#184f95",
    "non-SFHA": "#eb6834",
}

fig, (ax_count, ax_pct, ax_price) = plt.subplots(1, 3, figsize=(19, 5))

years = sorted(df["policyYear"].unique())
year_ticks = years[::2]

for category, group in df.groupby("floodZoneCategory"):
    group = group.sort_values("policyYear")
    color = CATEGORICAL_COLORS.get(category, "#898781")
    ax_count.plot(
        group["policyYear"],
        group["n_policies"],
        marker="o",
        markersize=5,
        linewidth=2,
        color=color,
        label=category,
    )

ax_count.set_ylim(bottom=0)
ax_count.set_xticks(year_ticks)
ax_count.set_xlabel("Policy year")
ax_count.set_ylabel("Number of policies")
ax_count.set_title("Policy count by year and flood zone category")
ax_count.grid(True, color="#e1e0d9", linewidth=0.8)
ax_count.spines[["top", "right"]].set_visible(False)
ax_count.legend(title="Flood zone category", frameon=False)

for category, group in df.groupby("floodZoneCategory"):
    group = group.sort_values("policyYear")
    color = CATEGORICAL_COLORS.get(category, "#898781")
    ax_pct.plot(
        group["policyYear"],
        group["pct_elevated"],
        marker="o",
        markersize=5,
        linewidth=2,
        color=color,
        label=category,
    )

ax_pct.set_ylim(bottom=0)
ax_pct.set_xticks(year_ticks)
ax_pct.set_xlabel("Policy year")
ax_pct.set_ylabel("% elevated")
ax_pct.set_title("Elevated building rate by flood zone category and year")
ax_pct.grid(True, color="#e1e0d9", linewidth=0.8)
ax_pct.spines[["top", "right"]].set_visible(False)
ax_pct.legend(title="Flood zone category", frameon=False)

for category, group in df.groupby("floodZoneCategory"):
    group = group.sort_values("policyYear")
    color = CATEGORICAL_COLORS.get(category, "#898781")
    ax_price.plot(
        group["policyYear"],
        group["price_per_dollar_coverage"],
        marker="o",
        markersize=5,
        linewidth=2,
        color=color,
        label=category,
    )

ax_price.set_ylim(bottom=0)
ax_price.set_xticks(year_ticks)
ax_price.set_xlabel("Policy year")
ax_price.set_ylabel("Policy cost per $ of coverage")
ax_price.set_title("Weighted avg. price per $ insured by year and flood zone")
ax_price.grid(True, color="#e1e0d9", linewidth=0.8)
ax_price.spines[["top", "right"]].set_visible(False)
ax_price.legend(title="Flood zone category", frameon=False)

plt.tight_layout()
fig.savefig(figures_dir / "adaptation_by_flood_zone_over_time.png", dpi=200)
plt.show()

# %% 4. Bar plot: adaptation by flood zone and construction period (2024 cross section)

FIRM_COLORS = {
    "Pre-FIRM": "#86b6ef",
    "Post-FIRM": "#184f95",
}

df_2024_plot = df_2024.dropna(subset=["postFIRMConstructionIndicator"]).copy()
df_2024_plot["firmPeriod"] = df_2024_plot["postFIRMConstructionIndicator"].map({1: "Post-FIRM", 0: "Pre-FIRM"})

categories = sorted(df_2024_plot["floodZoneCategory"].unique())
firm_periods = ["Pre-FIRM", "Post-FIRM"]
bar_width = 0.35
x_positions = range(len(categories))

fig, (ax_count, ax_pct, ax_price) = plt.subplots(1, 3, figsize=(19, 5))

for i, firm_period in enumerate(firm_periods):
    period_data = df_2024_plot[df_2024_plot["firmPeriod"] == firm_period].set_index("floodZoneCategory")
    counts = [period_data["n_policies"].get(cat, 0) for cat in categories]
    offsets = [xi + (i - 0.5) * bar_width for xi in x_positions]
    ax_count.bar(offsets, counts, width=bar_width, color=FIRM_COLORS[firm_period], label=firm_period)

ax_count.set_xticks(list(x_positions))
ax_count.set_xticklabels(categories)
ax_count.set_ylim(bottom=0)
ax_count.set_xlabel("Flood zone category")
ax_count.set_ylabel("Number of policies")
ax_count.set_title("Policy count by flood zone and construction period (2024)")
ax_count.grid(True, axis="y", color="#e1e0d9", linewidth=0.8)
ax_count.spines[["top", "right"]].set_visible(False)
ax_count.legend(title="Construction period", frameon=False)

for i, firm_period in enumerate(firm_periods):
    period_data = df_2024_plot[df_2024_plot["firmPeriod"] == firm_period].set_index("floodZoneCategory")
    values = [period_data["pct_elevated"].get(cat, 0) for cat in categories]
    offsets = [xi + (i - 0.5) * bar_width for xi in x_positions]
    ax_pct.bar(offsets, values, width=bar_width, color=FIRM_COLORS[firm_period], label=firm_period)

ax_pct.set_xticks(list(x_positions))
ax_pct.set_xticklabels(categories)
ax_pct.set_ylim(bottom=0)
ax_pct.set_xlabel("Flood zone category")
ax_pct.set_ylabel("% elevated")
ax_pct.set_title("Elevated building rate by flood zone and construction period (2024)")
ax_pct.grid(True, axis="y", color="#e1e0d9", linewidth=0.8)
ax_pct.spines[["top", "right"]].set_visible(False)
ax_pct.legend(title="Construction period", frameon=False)

for i, firm_period in enumerate(firm_periods):
    period_data = df_2024_plot[df_2024_plot["firmPeriod"] == firm_period].set_index("floodZoneCategory")
    values = [period_data["price_per_dollar_coverage"].get(cat, 0) for cat in categories]
    offsets = [xi + (i - 0.5) * bar_width for xi in x_positions]
    ax_price.bar(offsets, values, width=bar_width, color=FIRM_COLORS[firm_period], label=firm_period)

ax_price.set_xticks(list(x_positions))
ax_price.set_xticklabels(categories)
ax_price.set_ylim(bottom=0)
ax_price.set_xlabel("Flood zone category")
ax_price.set_ylabel("Policy cost per $ of coverage")
ax_price.set_title("Price per $ insured by flood zone and construction period (2024)")
ax_price.grid(True, axis="y", color="#e1e0d9", linewidth=0.8)
ax_price.spines[["top", "right"]].set_visible(False)
ax_price.legend(title="Construction period", frameon=False)

plt.tight_layout()
fig.savefig(figures_dir / "adaptation_by_flood_zone_2024_cross_section.png", dpi=200)
plt.show()

# %% 5. Descriptive statistics for floodproofedIndicator

df_floodproofed = pd.read_sql_query("""
    SELECT floodproofedIndicator, COUNT(*) AS n_policies
    FROM policies_sample
    WHERE occupancyType IN (1, 11) -- Only single-family residential buildings
    GROUP BY floodproofedIndicator
    ORDER BY floodproofedIndicator;
    """,
    conn
)
df_floodproofed["pct"] = 100 * df_floodproofed["n_policies"] / df_floodproofed["n_policies"].sum()

print(df_floodproofed)

# %%