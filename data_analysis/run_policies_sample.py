# %% Import packages

import pandas as pd
import sqlite3

# %% Connect to database

db_name = "C:\\Users\\dschm\\Documents\\Data\\FEMA\\fema.db"

conn = sqlite3.connect(db_name)
cursor = conn.cursor()

# %% Create policies_sample table

cursor.execute("""
CREATE TABLE policies_sample AS
SELECT * FROM policies
WHERE (rowid % 100) = 0;
""")

conn.commit()

print("policies_sample table created successfully")

# %% Check that table is present

cursor.execute("""
SELECT name FROM sqlite_master 
WHERE type='table' AND name='policies_sample';
""")

if cursor.fetchone():
    print("✓ policies_sample table exists")
    
    # Get row count
    cursor.execute("SELECT COUNT(*) FROM policies_sample;")
    row_count = cursor.fetchone()[0]
    print(f"✓ Table contains {row_count} rows")
else:
    print("✗ policies_sample table not found")

# %% Close connection

conn.close()
# %%
