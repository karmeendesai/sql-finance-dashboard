import sqlite3
import pandas as pd
from pathlib import Path

# paths
DB_PATH = Path("data/finance.db")
CSV_PATH = Path("data/sample_transactions.csv")

# connecting to database (creates the database if it doesnt exist)
conn = sqlite3.connect(DB_PATH)
cursor = conn.cursor()

# drop table if it already exists (so we can reset)
cursor.execute("DROP TABLE IF EXISTS transactions")

# create table
cursor.execute("""
CREATE TABLE transactions (
    transaction_ID INTEGER PRIMARY KEY AUTOINCREMENT,
    transaction_date TEXT,
    merchant TEXT,
    category_name TEXT,
    amount REAL,
    transaction_type TEXT,
    notes TEXT
)
""")

# load CSV into pandas
df = pd.read_csv(CSV_PATH)

# insert into SQL table
df.to_sql("transactions", conn, if_exists="append", index=False)

# commit and close
conn.commit()

print("Tables:", conn.execute("SELECT name FROM sqlite_master WHERE type='table';").fetchall())

print("Rows:", conn.execute("SELECT COUNT(*) FROM transactions;").fetchone()[0])

conn.close()

print("Database created successfully.")