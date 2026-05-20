from datetime import date


# Converts expiry dates into simple status labels.
def expiry_status(expiration_date):
    if expiration_date is None:
        return "unknown"

    today = date.today()
    days_left = (expiration_date - today).days

    if days_left < 0:
        return "expired"

    if days_left <= 3:
        return "urgent"

    if days_left <= 7:
        return "soon"

    return "safe"


# Creates readable expiry text for the UI.
def expiry_label(expiration_date):
    if expiration_date is None:
        return "No date"

    today = date.today()
    days_left = (expiration_date - today).days

    if days_left < 0:
        return f"Expired {-days_left} day(s) ago"

    if days_left == 0:
        return "Expires today"

    if days_left == 1:
        return "Expires tomorrow"

    return f"Expires in {days_left} days"