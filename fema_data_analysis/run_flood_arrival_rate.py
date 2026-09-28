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
 
# Group rated flood zones: A = SFHA, V = coastal SFHA, X/B/C = outside SFHA
ZONE = """CASE substr(ratedFloodZone, 1, 1)
            WHEN 'A' THEN 'A' WHEN 'V' THEN 'V'
            WHEN 'X' THEN 'X/B/C' WHEN 'B' THEN 'X/B/C' WHEN 'C' THEN 'X/B/C'
            ELSE 'Other' END"""
 
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
print(rates.round(4))
 
# Pooled rate per zone over all years with policy data
pooled = df.dropna().groupby("zone")[["n_claims", "n_policies"]].sum()
pooled["rate"] = pooled["n_claims"] / pooled["n_policies"]
print(pooled)
 
rates.to_csv(DATA_DIR / "flood_arrival_rates_by_zone.csv")