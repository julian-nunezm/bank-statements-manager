from datetime import date, timedelta

def calculate_future_credit_card_statements() -> list:
    one_day_delta = timedelta(days=1)
    four_weeks_delta = timedelta(weeks=4)

    initial_start_date = date(2026, 5, 13)
    initial_end_date = date(2026, 5, 20)

    statements = [
        {"start_date": initial_start_date, "end_date": initial_end_date,},
    ]

    while statements[-1].get("end_date").year < 2027:
        last_statement = statements[-1]
        new_start_date = last_statement.get("end_date") + one_day_delta
        new_end_date = new_start_date + four_weeks_delta
        statements.append({"start_date": new_start_date, "end_date": new_end_date,})
    
    print(statements)
    return statements