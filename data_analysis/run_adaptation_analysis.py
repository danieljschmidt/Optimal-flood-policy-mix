# %% Import packages

import pandas as pd
import sqlite3

# %% Connect to database

db_name = "C:\\Users\\dschm\\Documents\\Data\\FEMA\\fema.db"

conn = sqlite3.connect(db_name)

# %% 1. Elevated building rate by flood zone

df = pd.read_sql_query("""
    SELECT
        CASE
            WHEN UPPER(TRIM(ratedFloodZone)) LIKE 'A%' OR UPPER(TRIM(ratedFloodZone)) LIKE 'V%' THEN 'SFHA'
            WHEN UPPER(TRIM(ratedFloodZone)) IN ('B', 'C', 'D', 'X') THEN 'non-SFHA'
            WHEN ratedFloodZone IS NULL THEN 'Unknown'
            ELSE UPPER(TRIM(ratedFloodZone))
        END AS floodZoneCategory,
        COUNT(*)                                   AS n_policies,
        AVG(CASE WHEN elevatedBuildingIndicator = 1 THEN 1.0 WHEN elevatedBuildingIndicator = 0 THEN 0.0 ELSE NULL END) AS pct_elevated,
        AVG(CASE WHEN elevationCertificateIndicator = 1 THEN 1.0 WHEN elevationCertificateIndicator = 0 THEN 0.0 ELSE NULL END) AS pct_has_ec,        SUM(CASE WHEN ratedFloodZone IS NULL THEN 1 ELSE 0 END) AS n_null_flood_zone,
        SUM(CASE WHEN elevatedBuildingIndicator IS NULL THEN 1 ELSE 0 END) AS n_null_elevated
    FROM policies_sample
    GROUP BY floodZoneCategory
    ORDER BY n_policies DESC;
    """,
    conn
)

print(df)

# %% 2. Show frequency of elevation certificate indicator values

# Better to ignore this variable, not central to the analysis

# Elevation Certificate Indicator Values:
# 1 - No Elevation Certificate, original effective date prior to October 1, 1982, with no break in insurance coverage or change in insurable interest. Policies will be rated using 'No Base Flood Elevation' +2 to +4 feet rates;
# 2 - No Elevation Certificate, original effective date on or after October 1, 1982, with no break in insurance coverage or change in insurable interest. Policies will be rated using 'No Elevation Certificate' rates;
# 3 - Elevation Certificate with BFE. Policies will be rated using 'With Base Flood Elevation' rates;
# 4 - Elevation Certificate without BFE. Policies will be rated using 'No Base Flood Elevation' rates;
# A - Basement or Subgrade Crawlspace;
# B - Fill or Crawlspace;
# C - Piles, Piers, or Columns with Enclosure;
# D - Piles, Piers, or Columns without Enclosure;
# E - Slab on Grade;

df_elevated_ec = pd.read_sql_query("""
    SELECT
        elevatedBuildingIndicator,
        elevationCertificateIndicator,
        COUNT(*) AS count,
        ROUND(100.0 * COUNT(*) / SUM(COUNT(*)) OVER (PARTITION BY elevatedBuildingIndicator), 2) AS pct_within_elevated
    FROM policies_sample
    GROUP BY elevatedBuildingIndicator, elevationCertificateIndicator
    ORDER BY elevatedBuildingIndicator, count DESC;
    """,
    conn
)

print("\nCross-Tabulation: Elevated Building Indicator vs Elevation Certificate Indicator:")
print(df_elevated_ec)

# %%
