import json, pandas as pd, numpy as np
from quiffen import Qif, QifDataType, TransactionLike
from datetime import date

from common.constants import *
from common.db_functions import insert_transactions

# https://pypi.org/project/quiffen/
# https://quiffen.readthedocs.io/en/latest/

def categorise_transaction(transaction:TransactionLike) -> str:
    payee = transaction.payee.lower()#.split(" ")
    categories = {
        FOOD: ["afloat", "yo- chi", "st rose", "el manglar gastro bar"],
        TRANSPORT: ["easypark", "eg group"],
        HEALTH: ["chemist"],
        GROCERIES: ["andres j leal galvis", "liquorland", "coles"],
        BILLS: ["seene", "lightning broadband"],
        UNFORESEEN: ["raiz maint fee"],
        INVESTMENTS: ["raiz investment"],
        RECYCLING: ["tomra"],
        BETTER_TOGETHER: ["recycling"],
        PURCHASES: ["ikea"]
    }

    for category, values in categories.items():
        found = any(item in payee for item in values)
        if found:
            return category #if found else transaction.category

    return transaction.category if transaction.category else "Uncategorised"

def get_tx_from_qif_file(path:str) -> pd.DataFrame:
    qif = Qif.parse(path, day_first=True)
    df = pd.DataFrame(qif.to_dataframe(data_type=QifDataType.TRANSACTIONS))
    return df

def wrangle_tx(df:pd.DataFrame) -> pd.DataFrame:
    # Remove all the NULL columns except the 'category' one
    cols_to_drop = df.isna().any()
    cols_to_drop['category'] = False
    cols_to_drop['splits'] = True
    cols_to_drop['line_number'] = True
    # print(cols_to_drop.index)
    df = df.loc[:, ~cols_to_drop]
    return df

def reset_tx_dates(df:pd.DataFrame) -> pd.DataFrame:
    # The date in the QIF transaction might not be the real one when the tx happened.
    # Evaluate a regex for 'Date 30 Apr 2026' in the payee value.
    # If there's no such value, use the one in the QIF tx.
    regex_pattern = r"(Date\s\d\d\s[A-Za-z]+\s[0-9]+)"
    # print(df["payee"].str.extract(regex_pattern))
    df["internal_date"] = df["payee"].str.extract(regex_pattern)
    df["internal_date"] = pd.to_datetime(df["internal_date"].str.replace('Date ', ''), format='%d %b %Y')
    df["original_date"] = df["date"]
    df["date"] = df["internal_date"].combine_first(df["date"])
    # print(df.tail(30))
    return df

def monitor_balances(statements:list) -> None:
    everydays_balance = 0
    credit_cards_balance = 0    

    for statement in statements:
        bank = statement.get("bank")
        account = statement.get("account")
        balance_prior_day = statement.get("balance_prior_day")
        type = statement.get("type")
        filepath = statement.get("filepath")
        filename = statement.get("filename")
        start_date = statement.get("start_date")
        end_date = statement.get("end_date")

        # print("-" * 60)
        # print(f"Analysing {account} ({bank}) statement...")
        # print(f"Timeframe from {start_date} to {end_date}")
        # print(f"{filepath}{filename}")

        tx_df = get_tx_from_qif_file(f"{filepath}{filename}")
        tx_df = wrangle_tx(tx_df)
        tx_df = reset_tx_dates(tx_df)
        
        tx_df = tx_df[(tx_df["date"] >= start_date) & (tx_df["date"] <= end_date)]
        message = f"{bank} {account} transactions from {start_date} to {end_date}: {len(tx_df.index):,}"
        print("-"*len(message), f"{message}", "-"*len(message), sep="\n")
        print(tx_df)

        if bank == "CBA Bank" and account == "Credit Card":
            # tx_df["date"] = pd.to_datetime(tx_df["date"])
            insert_transactions(1194, tx_df, are_paid=True)
        
        balance = balance_prior_day + tx_df["amount"].sum()
        print("--", f"Balance: ${balance:,.2F}", "--", sep="\n")

        if type == "Everyday":
            everydays_balance += balance
        elif type == "Credit Card":
            credit_cards_balance += balance

    # print("\n", "-" * 60)
    print(f"Credit cards balance: ${credit_cards_balance:,.2F}")
    print(f"Everyday accounts balance: ${everydays_balance:,.2F}")
    final_balance = everydays_balance + credit_cards_balance
    print(f"Final balance: ${final_balance:,.2F} ({"✅ All good!" if final_balance > 0 else "❌ Review!"})", "\n")

if __name__ == "__main__":
    statements = [
        {
            "bank": "ING Bank",
            "type": "Everyday",
            "account": "Everyday account",
            "balance_prior_day": 233.0,
            "filepath": "files/ing/",
            "filename": "ing_transactions.qif",
            "start_date": "2026-05-13",
            "end_date": "2026-05-20",
        },
        {
            "bank": "CBA Bank",
            "account": "Everyday account (Karen)",
            "balance_prior_day": 2352.94,
            "type": "Everyday",
            "filepath": "files/cba/karen/",
            "filename": "cba_transactions.qif",
            "start_date": "2026-05-13",
            "end_date": "2026-05-20",
        },
        {
            "bank": "CBA Bank",
            "account": "Credit Card",
            "balance_prior_day": 0.0,
            "type": "Credit Card",
            "filepath": "files/cba/credit_card/",
            "filename": "cba_transactions.qif",
            "start_date": "2026-05-13",
            "end_date": "2026-05-18",               # Based on the statement, it's 20th but the transactions included were till 18th
            "statement_periods": [
                {
                    "from": date(2026, 5, 13),
                    "to": date(2026, 5, 20),
                },
                {
                    "from": date(2026, 5, 21),
                    "to": date(2026, 6, 18),
                },
            ]
        },
    ]
    
    monitor_balances(statements)
