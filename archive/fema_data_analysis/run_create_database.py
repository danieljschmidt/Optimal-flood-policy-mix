import pandas as pd
import sqlite3
import gc

from database_setup_claims import claims_dtype_dict, claims_date_cols
from database_setup_policies import policies_dtype_dict, policies_date_cols

csv_file_claims = "C:\\Data\\FEMA\\FimaNfipClaims_v2.csv"
csv_file_policies = "C:\\Data\\FEMA\\FimaNfipPolicies.csv"
db_name = "C:\\Data\\FEMA\\fema.db"
table_name_claims = "claims"
table_name_policies = "policies"
chunk_size = 500_000 

conn = sqlite3.connect(db_name)

# CLAIMS

chunks_claims = pd.read_csv(
    csv_file_claims, 
    usecols=list(claims_dtype_dict.keys()) + claims_date_cols,
    dtype=claims_dtype_dict,
    parse_dates=claims_date_cols,
    chunksize=chunk_size
)

print(f"Processing {csv_file_claims} in chunks of {chunk_size} rows...")
chunk_count = 0
for chunk in chunks_claims:
    chunk_count += 1
    print(f"Chunk {chunk_count} ({len(chunk)} rows)")
    if_exists_mode = 'replace' if chunk_count == 1 else 'append'
    chunk.to_sql(table_name_claims, conn, if_exists=if_exists_mode, index=False)
    del chunk
    gc.collect()

claims_nrows = pd.read_sql_query(
    "SELECT COUNT(id) FROM claims", 
    conn
)
claims_cols = pd.read_sql_query("PRAGMA table_info(claims)", conn)
print(f"Claims data loaded successfully: {claims_nrows.values[0][0]} rows, {len(claims_cols)} columns")

# POLICIES

chunks_policies = pd.read_csv(
    csv_file_policies, 
    usecols=list(policies_dtype_dict.keys()) + policies_date_cols,
    dtype=policies_dtype_dict,
    parse_dates=policies_date_cols,
    chunksize=chunk_size
)

print(f"Processing {csv_file_policies} in chunks of {chunk_size} rows...")  
chunk_count = 0
for chunk in chunks_policies:
    chunk_count += 1
    print(f"Chunk {chunk_count} ({len(chunk)} rows)")
    if_exists_mode = 'replace' if chunk_count == 1 else 'append'
    chunk.to_sql(table_name_policies, conn, if_exists=if_exists_mode, index=False)
    del chunk
    gc.collect()

policies_nrows = pd.read_sql_query(
    "SELECT COUNT(id) FROM policies",
    conn
)
policies_cols = pd.read_sql_query("PRAGMA table_info(policies)", conn)
print(f"Policies data loaded successfully: {policies_nrows.values[0][0]} rows, {len(policies_cols)} columns")

conn.close()