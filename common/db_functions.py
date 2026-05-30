import sqlite3

def connect_to_db() -> sqlite3.Connection:
    # print("Connecting to DB...")
    conn = sqlite3.connect("db/personal_finances.db")
    return conn

def validate_db_tables() -> bool:
    conn = connect_to_db()
    cursor = conn.cursor()

    query = "SELECT name FROM sqlite_master WHERE type='table';"
    cursor.execute(query)
    records = cursor.fetchall()
    return len(records) > 0

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
        dml_query = "CREATE TABLE IF NOT EXISTS statement_periods (account_id INTEGER NOT NULL, start_date TEXT NOT NULL, end_date TEXT NOT NULL, PRIMARY KEY(account_id, start_date))"
        cursor.execute(dml_query)
    except Exception as exc:
        print(f"Error! {exc}")
    else:
        print("Table 'accounts' created successfully.")
    
    # TODO: Transactions table
    
    conn.close()

def insert_main_records() -> None:
    print("\nInserting main records...\n")
    conn = connect_to_db()
    cursor = conn.cursor()
    
    try:
        last_digits = input("- Please enter the last digits from the account/card:\n")
        name = input("- Please enter the name for the account/card:\n")
        type = input("- Please enter the type for the account/card (Credit Card, Debit Card):\n")
        description = input("- Please enter the description for the account/card:\n")
        
        account_data = (last_digits, name, type, description)
        query = "INSERT INTO accounts (id, name, type, description) VALUES (?, ?, ?, ?)"
        cursor.execute(query, account_data)
    except Exception as exc:
        print(f"Error! {exc}")
    else:
        print("\nRecords created successfully!\n")

    try:
        last_digits = input("- Please enter the last digits from the account/card:\n")
        start_date = str(input("- Please enter the start date (YYYY-MM-DD) for the statement period:\n"))
        end_date = str(input("- Please enter the end date (YYYY-MM-DD) for the statement period:\n"))
        print(start_date, end_date)

        query = f"INSERT INTO statement_periods (account_id, start_date, end_date) VALUES ({last_digits}, '{start_date}', '{end_date}')"
        cursor.execute(query)
    except Exception as exc:
        print(f"Error! {exc}")
    else:
        print("\nRecords created successfully!\n")
    
    # TODO: Transactions table records

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
        print(row, type(row))
    
    conn.close()
    return records

def get_accounts() -> list: return get_records("accounts")

def get_statement_periods() -> list: return get_records("statement_periods")