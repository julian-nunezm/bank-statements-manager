import sqlite3
import pandas as pd
from .finances import calculate_future_credit_card_statements

def connect_to_db() -> sqlite3.Connection:
    # print("Connecting to DB...")
    conn = sqlite3.connect("db/personal_finances.db")
    return conn

def validate_db_tables() -> bool:
    conn = connect_to_db()
    cursor = conn.cursor()

    query = "SELECT name FROM sqlite_master WHERE type='table';"
    cursor.execute(query)
    tables_created = cursor.fetchall()
    # So far there should be 3 tables: Accounts, Statement Periods, and Transactions
    return len(tables_created) >= 3

def create_tables() -> None:
    print("\nCreating tables...")
    conn = connect_to_db()
    cursor = conn.cursor()
    
    try:
        dml_query = "CREATE TABLE IF NOT EXISTS accounts (id INTEGER PRIMARY KEY, name TEXT NOT NULL, type TEXT NOT NULL, description TEXT)"
        cursor.execute(dml_query)
    except Exception as exc:
        print(f"Error! {exc}")
    else:
        print("Table 'accounts' created successfully.")
    
    try:
        dml_query = "CREATE TABLE IF NOT EXISTS statement_periods (account_id INTEGER NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL, real_end_date TEXT, PRIMARY KEY(account_id, start_date))"
        cursor.execute(dml_query)
    except Exception as exc:
        print(f"Error! {exc}")
    else:
        print("Table 'statement_periods' created successfully.")
    
    try:
        dml_query = "CREATE TABLE IF NOT EXISTS transactions (account_id INTEGER NOT NULL, date TEXT NOT NULL, amount REAL NOT NULL, Description TEXT NOT NULL, real_end_date TEXT, is_paid BOOLEAN DEFAULT 0, PRIMARY KEY(account_id, date, amount, description))"
        cursor.execute(dml_query)
    except Exception as exc:
        print(f"Error! {exc}")
    else:
        print("Table 'transactions' created successfully.")
    
    conn.close()

def delete_table(table:str) -> None:
    print(f"Deleting the '{table}' table.")
    try:
        with sqlite3.connect("db/personal_finances.db") as conn:
            cursor = conn.cursor()
            cursor.execute(f"DROP TABLE IF EXISTS {table}")
    except Exception as exc:
        print(f"Error! {exc}")
    else:
        print("Done.\n")
    

def insert_main_records() -> None:
    insert_account = input("-> Do you want to insert a new card? Y/N: \n") == "Y"
    
    if insert_account:
        print("\nInserting main records...\n")
        conn = connect_to_db()
        cursor = conn.cursor()

        last_digits = input("- Please enter the last 4 digits from the account/card:\n")
        name = input("- Please enter the name for the account/card:\n")
        type = input("- Please enter the type for the account/card (Credit Card, Debit Card):\n")
        description = input("- Please enter the description for the account/card:\n")
        
        try:
            account_data = (last_digits, name, type, description)
            query = "INSERT INTO accounts (id, name, type, description) VALUES (?, ?, ?, ?)"
            cursor.execute(query, account_data)
        except Exception as exc:
            print(f"Error! {exc}")
        else:
            print("\nRecords created successfully!\n")

        print(f"\n-> Creating statement periods for {type} ending in {last_digits}...\n")
        statements = calculate_future_credit_card_statements()
        try:
            new_rows = []
            for statement in statements:
                start_date = statement.get("start_date")
                end_date = statement.get("end_date")
                new_row = (last_digits, start_date.strftime("%Y-%m-%d"), end_date.strftime("%Y-%m-%d"))
                new_rows.append(new_row)

            # last_digits = input("- Please enter the last digits from the account/card:\n")
            # start_date = str(input("- Please enter the start date (YYYY-MM-DD) for the statement period:\n"))
            # end_date = str(input("- Please enter the end date (YYYY-MM-DD) for the statement period:\n"))
            # print(start_date, end_date)

            # query = f"INSERT INTO statement_periods (account_id, start_date, end_date) VALUES ({last_digits}, '{start_date}', '{end_date}')"
            query = f"INSERT INTO statement_periods (account_id, start_date, end_date) VALUES (?, ?, ?)"
            cursor.executemany(query, new_rows)
        except Exception as exc:
            print(f"Error! {exc}")
        else:
            print("\nRecords created successfully!\n")
    
        conn.commit()
        conn.close()

def insert_transactions(account_id:int, tx_df:pd.DataFrame, are_paid:False) -> None:
    print(f"\nInserting {len(tx_df.index)} transactions on account ending in {account_id}...\n")
    conn = connect_to_db()
    cursor = conn.cursor()

    try:
        new_rows = []
        for tx in tx_df.itertuples():
            # transactions (account_id INTEGER NOT NULL, date TEXT NOT NULL, amount REAL NOT NULL, description TEXT NOT NULL, real_end_date TEXT, is_paid BOOLEAN DEFAULT 0, PRIMARY KEY(account_id, date, amount, description))"
            # .strftime("%Y-%m-%d")
            new_row = (account_id, tx.date.strftime("%Y-%m-%d"), tx.amount, tx.payee, None, are_paid)
            # print(type(account_id), account_id, type(tx.date), tx.date, type(tx.amount), tx.amount, type(tx.payee), tx.payee)
            new_rows.append(new_row)

        # last_digits = input("- Please enter the last digits from the account/card:\n")
        # start_date = str(input("- Please enter the start date (YYYY-MM-DD) for the statement period:\n"))
        # end_date = str(input("- Please enter the end date (YYYY-MM-DD) for the statement period:\n"))
        # print(start_date, end_date)

        query = f"INSERT OR IGNORE INTO transactions (account_id, date, amount, description, real_end_date, is_paid) VALUES (?, ?, ?, ?, ?, ?)"
        cursor.executemany(query, new_rows)
    except Exception as exc:
        print(f"Error! {exc}")
    else:
        print("\nRecords created successfully!\n")

    conn.commit()
    conn.close()

def get_records(table:str) -> list:
    table_parts = table.split("_")
    table_parts = [word.title() for word in table_parts]
    print(f"\nQuering {' '.join(table_parts)}...")
    
    conn = connect_to_db()
    cursor = conn.cursor()

    cursor.execute(f"SELECT * FROM {table};")
    records = cursor.fetchall()
    
    for row in records:
        # print(row, type(row))
        print(row)
    
    conn.close()
    return records

def get_accounts() -> list: return get_records("accounts")

def get_statement_periods() -> list: return get_records("statement_periods")

def get_accounts_statement_periods() -> list:
    print(f"\nQuering Account Statement Periods...")
    conn = connect_to_db()
    cursor = conn.cursor()

    query = """
SELECT a.*, sp.*
FROM accounts a
INNER JOIN statement_periods sp ON a.id = sp.account_id;
"""

    cursor.execute(query)
    records = cursor.fetchall()
    
    for row in records:
        print(row, type(row))
    
    conn.close()
    return records

def get_transactions() -> list: return get_records("transactions")

def get_account_balance(account_id:int, paid_tx:True) -> list:
    print(f"\nQuering transactions for account ending with {account_id}...")
    conn = connect_to_db()
    cursor = conn.cursor()

    query = f"""
SELECT SUM(amount)
FROM transactions
WHERE account_id = {account_id}
AND is_paid = {int(paid_tx)};
"""

    cursor.execute(query)
    records = cursor.fetchall()
    
    balance = records[0][0] if records[0][0] else 0.0
    print(balance)
    
    conn.close()
    return records

def execute_db_functions():
    if not validate_db_tables():
        create_tables()
        insert_main_records()

    get_accounts()
    get_statement_periods()
    # get_accounts_statement_periods()

    # Transactions
    get_transactions()
    get_account_balance(1194, True)

    # Delete table
    # delete_table("transactions")
