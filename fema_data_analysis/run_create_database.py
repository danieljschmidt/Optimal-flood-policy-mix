import pandas as pd
import pyarrow.dataset as ds
import sqlite3
import gc
from pathlib import Path

from database_setup_claims import claims_dtype_dict, claims_date_cols
from database_setup_policies import policies_dtype_dict, policies_date_cols

DATA_DIR = Path(r"C:\Users\TPRINS\OneDrive - UvA\Documenten\Python files insurance-aid\Code August 2026\fema_data_analysis\data")
parquet_claims = DATA_DIR / "NfipClaimsV3.parquet"        # a file OR a folder of .parquet parts
parquet_policies = DATA_DIR / "NfipPoliciesV3.parquet"
db_name = DATA_DIR / "fema.db"
table_name_claims = "claims"
table_name_policies = "policies"
chunk_size = 500_000


def load_parquet_to_sql(path, table_name, conn, dtype_dict, date_cols):
    """Read a parquet file (or folder of parquet parts) in batches into a SQL table."""
    dataset = ds.dataset(path, format="parquet")
    wanted = list(dtype_dict.keys()) + date_cols
 
    missing = [c for c in wanted if c not in dataset.schema.names]
    if missing:
        raise SystemExit(
            f"{Path(path).name} does not contain {missing}\n"
            f"Columns actually present: {dataset.schema.names}"
        )
 
    print(f"Processing {path} in chunks of {chunk_size} rows...")
    chunk_count = 0
    for batch in dataset.to_batches(columns=wanted, batch_size=chunk_size):
        chunk_count += 1
        chunk = batch.to_pandas()
        print(f"Chunk {chunk_count} ({len(chunk)} rows)")
 
        # parquet already carries its own types; re-cast so the SQL schema matches
        # what the CSV version produced. Cast column by column so a bad dtype
        # names the column instead of failing anonymously.
        for col, dt in dtype_dict.items():
            try:
                chunk[col] = chunk[col].astype(dt)
            except (TypeError, ValueError) as err:
                bad = pd.to_numeric(chunk[col], errors="coerce").dropna()
                raise SystemExit(
                    f"Column '{col}' will not cast to {dt}: {err}\n"
                    f"  values seen here: min={bad.min()}, max={bad.max()}, "
                    f"example={bad.head(3).tolist()}"
                )
 
        for col in date_cols:
            chunk[col] = pd.to_datetime(chunk[col], errors="coerce")
 
        # v3 policies dropped countyCode; the first 5 digits of censusGeoid are
        # the county FIPS. No-op for claims, which still has a real countyCode.
        if "countyCode" not in chunk.columns and "censusGeoid" in chunk.columns:
            chunk["countyCode"] = chunk["censusGeoid"].str[:5]
 
        if_exists_mode = 'replace' if chunk_count == 1 else 'append'
        chunk.to_sql(table_name, conn, if_exists=if_exists_mode, index=False)
        del chunk, batch
        gc.collect()
 
 
conn = sqlite3.connect(db_name)
 
# CLAIMS
 
load_parquet_to_sql(
    parquet_claims, table_name_claims, conn, claims_dtype_dict, claims_date_cols
)
 
claims_nrows = pd.read_sql_query(
    "SELECT COUNT(id) FROM claims",
    conn
)
claims_cols = pd.read_sql_query("PRAGMA table_info(claims)", conn)
print(f"Claims data loaded successfully: {claims_nrows.values[0][0]} rows, {len(claims_cols)} columns")
 
# POLICIES
 
load_parquet_to_sql(
    parquet_policies, table_name_policies, conn, policies_dtype_dict, policies_date_cols
)
 
policies_nrows = pd.read_sql_query(
    "SELECT COUNT(id) FROM policies",
    conn
)
policies_cols = pd.read_sql_query("PRAGMA table_info(policies)", conn)
print(f"Policies data loaded successfully: {policies_nrows.values[0][0]} rows, {len(policies_cols)} columns")
 
# COUNTY CODE SANITY CHECKS
 
# 1. Claims has BOTH censusGeoid and a real countyCode, so the derivation rule
#    used for policies can be verified directly where the truth is known.
check = pd.read_sql_query(
    """
    SELECT COUNT(*) AS compared,
           SUM(CASE WHEN substr(censusGeoid, 1, 5) = countyCode THEN 1 ELSE 0 END) AS matching
    FROM claims
    WHERE censusGeoid IS NOT NULL AND countyCode IS NOT NULL
    """,
    conn
)
compared = int(check["compared"][0] or 0)
matching = int(check["matching"][0] or 0)
print(f"\nDerivation check on claims: {matching}/{compared} rows have "
      f"substr(censusGeoid,1,5) == countyCode"
      + ("  -> rule holds" if compared and matching == compared else "  -> RULE DOES NOT HOLD"))
 
# 2. The derived policies codes should look like the claims ones.
overlap = pd.read_sql_query(
    """
    SELECT (SELECT COUNT(DISTINCT countyCode) FROM claims)   AS claim_counties,
           (SELECT COUNT(DISTINCT countyCode) FROM policies) AS policy_counties,
           (SELECT COUNT(*) FROM (
                SELECT DISTINCT countyCode FROM policies
                WHERE countyCode IS NOT NULL
                  AND countyCode NOT IN (SELECT countyCode FROM claims)
            )) AS in_policies_only
    """,
    conn
)
print(overlap.to_string(index=False))
 
conn.close()