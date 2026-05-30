from common import db_functions as db

if __name__ == '__main__':
    if not db.validate_db_tables():
        db.create_tables()
        db.insert_main_records()

    db.get_accounts()
    db.get_statement_periods()