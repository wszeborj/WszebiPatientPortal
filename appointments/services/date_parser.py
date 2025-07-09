from datetime import datetime


def try_parsing_date(possible_date):
    possible_date = possible_date.strip()
    for fmt in ("%b. %d, %Y", "%b %d, %Y", "%B %d, %Y"):
        try:
            return datetime.strptime(possible_date, fmt).date()
        except ValueError:
            pass
    raise ValueError(f"Non-valid date format: '{possible_date}'")
