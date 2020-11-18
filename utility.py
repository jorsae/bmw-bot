import query

from datetime import datetime, date
from titles import HallOfFame

# Returns year + month in text format
def get_month():
    return datetime.now().strftime("%B")

# Returns boolean if user_id is in max_statmodel
def get_userid_in_max_statmodel(user_id, max_statmodel):
    for stat in max_statmodel:
        if stat.user_id.user_id == user_id:
            return True
    return False

# returns emote for the given HallOfFame title
def get_hof_emote(title):
    if title == HallOfFame.catches:
        return '<:BMW:767973944857985114>'
    if title == HallOfFame.legendary:
        return ':leg:'
    if title == HallOfFame.mythical:
        return ':unicorn:'
    if title == HallOfFame.ultrabeast:
        return ':cow:'
    if title == HallOfFame.shiny:
        return ':sparkles:'
    
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