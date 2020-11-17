from datetime import datetime, date

# returns true if the user is an admin. False otherwise
def is_admin(author, settings):
    if type(author) == str:
        return author in settings.admin
    else:
        return str(author) in settings.admin

# Converts a string to integer, defaults to 1
def str_to_int(value):
    try:
        return int(value)
    except:
        return 1

# Returns 1st of the current month
def get_date_current_month():
    now = datetime.now()
    return date(now.year, now.month, 1)

def get_date_forever_ago():
    return date(1000, 1, 1)