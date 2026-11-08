# -*- coding: utf-8 -*-
"""
Created on Thu Sep 24 16:27:30 2026

@author: tprins
"""

import sqlite3
import pandas as pd
from pathlib import Path
 
DATA_DIR = Path(r"C:\Users\TPRINS\OneDrive - UvA\Documenten\Python files insurance-aid\Code August 2026\fema_data_analysis\data")
conn = sqlite3.connect(DATA_DIR / "fema.db")
START, END = 2000, 2025
 
# Group rated flood zones: A = SFHA, V = coastal SFHA, Rest = everything else (X/B/C, D, missing)
ZONE = """CASE substr(ratedFloodZone, 1, 1)
            WHEN 'A' THEN 'A' WHEN 'V' THEN 'V'
            ELSE 'Rest' END"""
 
# Numerator: claims by year of loss
claims = pd.read_sql_query(f"""
    SELECT yearOfLoss AS year, {ZONE} AS zone, COUNT(*) AS n_claims
    FROM claims
    WHERE yearOfLoss BETWEEN {START} AND {END}
      -- AND buildingDamageAmount > 0   -- use the same filter as your damage distribution
    GROUP BY year, zone""", conn)
 
# Denominator: policies in force on 1 July (FEMA rule: effective <= date < termination)
policies = pd.read_sql_query(f"""
    WITH RECURSIVE years(year) AS (
        SELECT {START} UNION ALL SELECT year + 1 FROM years WHERE year < {END})
    SELECT y.year, {ZONE} AS zone, COUNT(*) AS n_policies
    FROM policies p CROSS JOIN years y
    WHERE substr(p.policyEffectiveDate, 1, 10) <= y.year || '-07-01'
      AND substr(p.policyTerminationDate, 1, 10) >  y.year || '-07-01'
    GROUP BY y.year, zone""", conn)
conn.close()
 
df = claims.merge(policies, on=["year", "zone"], how="left")
df["rate"] = df["n_claims"] / df["n_policies"]
 
rates = df.pivot(index="year", columns="zone", values="rate")

# Insured households (policies in force on 1 July) per zone and year
households = policies.pivot(index="year", columns="zone", values="n_policies")
print(households)

# Population shares: ~5% of the US population lives in A+V (NYU Furman Center, 2015, FEMA maps).
# Split A vs V by policies (both face mandatory purchase, so assume equal take-up).
SHARE_AV = 0.05
w_V = households["V"] / (households["A"] + households["V"])   # share of V within A+V
shares = pd.DataFrame({"A": SHARE_AV * (1 - w_V), "V": SHARE_AV * w_V, "Rest": 1 - SHARE_AV})
print(shares.round(4))

# Population-weighted rate in A+V (equals pooling A and V claims and policies).
# Rest is a single group, so its rate is already the population-weighted average there.
rates["A+V"] = (1 - w_V) * rates["A"] + w_V * rates["V"]
print(rates.round(4))
 
# Pooled rate per zone over all years with policy data
pooled = df.dropna().groupby("zone")[["n_claims", "n_policies"]].sum()
pooled.loc["A+V"] = pooled.loc[["A", "V"]].sum()
pooled["rate"] = pooled["n_claims"] / pooled["n_policies"]
print(pooled)

# Write a real Excel file (avoids locale problems with comma-separated CSV)
with pd.ExcelWriter(DATA_DIR / "flood_arrival_rates_by_zone.xlsx") as xl:
    rates.to_excel(xl, sheet_name="rates")
    households.to_excel(xl, sheet_name="insured households")
    shares.to_excel(xl, sheet_name="population shares")
    pooled.to_excel(xl, sheet_name="pooled")