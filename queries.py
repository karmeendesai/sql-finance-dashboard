import sqlite3
import pandas as pd
from pathlib import Path

# open queries.py
DB_PATH = Path(__file__).parent / "data" / "finance.db"

# runs sql query returning results as a dataframe
def run_query(query):
    conn = sqlite3.connect(DB_PATH)
    df = pd.read_sql_query(query, conn)
    conn.close()
    return df

# calculates total money spent
def total_spending():
    query = """
    SELECT SUM(amount) AS total_spent
    FROM transactions
    WHERE transaction_type = 'Expense'
    """
    return run_query(query)

# filters rows where transaction_type = 'Income' and adds up amount values
def total_income():
    query = """
    SELECT SUM(amount) AS total_income
    FROM transactions
    WHERE transaction_type = 'Income';
    """
    return run_query(query)

# breaks spending into categories
# (group rows by category - sort biggest to smallest )
def spending_by_category():
    query = """
    SELECT category_name, SUM(amount) AS total_spent
    FROM transactions
    WHERE transaction_type = 'Expense'
    GROUP BY category_name
    ORDER BY total_spent DESC;
    """
    return run_query(query)

# group spending by months (shows spending over time)
def monthly_spending():
    query = """
    SELECT substr(transaction_date, 1, 7) AS month, 
            SUM(amount) AS total_spent
    FROM transactions
    WHERE transaction_type = 'Expense'
    GROUP BY month
    ORDER BY month;
    """
    return run_query(query)

# filters income and groups income by months (income over time)
def monthly_income():
    query = """
    SELECT substr(transaction_date, 1, 7) AS month,
            SUM(amount) AS total_income
    FROM transactions
    wHERE transaction_type = 'Income'
    GROUP BY month
    ORDER BY month;
    """
    return run_query(query)

# categorize the big spenders, cuts down to 5 rows
def top_merchants():
    query = """
    SELECT merchant, COUNT(*) AS transaction_count,
            SUM(amount) AS total_amount
    FROM transactions
    WHERE transaction_type = 'Expense'
    GROUP BY merchant
    ORDER BY total_amount DESC
    LIMIT 5;
    """
    return run_query(query)

# cateogorize by transaction description
# returns everything in the table
def all_transactions():
    query = """
    SELECT transaction_date, merchant, category_name, amount, transaction_type, notes
    FROM transactions
    ORDER BY transaction_date DESC;
    """
    return run_query(query)