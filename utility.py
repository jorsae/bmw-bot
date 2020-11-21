import logging

import query
from datetime import datetime, date, timedelta
from enumeration import TimeFlag, HallOfFame
from models import UserStatModel

def parse_attribute_flags(**flags):
    if flags["legendary"]:
        return UserStatModel.legendary, 'Legendary'
    elif flags["mythical"]:
        return UserStatModel.mythical, 'Mythical'
    elif flags["ub"]:
        return UserStatModel.ultrabeast, 'Ultra beast'
    elif flags["shiny"]:
        return UserStatModel.shiny, 'Shiny'
    return UserStatModel.catches, 'Catches'

def parse_time_flags(**flags):
    date = get_date_current_month()
    if flags["all"]:
        return get_date_forever_ago(), TimeFlag.ALL
    if flags["week"]:
        return get_date_current_week(), TimeFlag.WEEK
    if flags["day"]:
        return date.today(), TimeFlag.DAY
    return date, TimeFlag.MONTH

# returns true if the user is an admin. False otherwise
def is_admin(author, admin_list):
    if type(author) == str:
        if author in admin_list:
            logging.warning(f'is_admin == true: {author}')
            return True
    else:
        if str(author) in admin_list:
            logging.warning(f'is_admin == true: {author}')
            return True
    return False

# returns emote for the given HallOfFame title
def get_hof_emote(title):
    if title == HallOfFame.catches:
        return '<:GoMedalPokedex:779248403502202901>'
    if title == HallOfFame.legendary:
        return '<:GoMedalLegendary:779249178525564947>'
    if title == HallOfFame.mythical:
        return '<:GoMedalMythical:779248236892258307>'
    if title == HallOfFame.ultrabeast:
        return '<:GoMedalUltrabeast:779247337977413642>'
    if title == HallOfFame.shiny:
        return '<:GoMedalShiny:779250293849587743>'
    
# Converts a string to integer, defaults to 1
def str_to_int(value):
    try:
        return int(value)
    except:
        return 1

def get_title_author_by_timeflag(timeflag):
    if timeflag == TimeFlag.ALL:
        return 'All time', 'Infinite'
    elif timeflag == TimeFlag.MONTH:
        today = date.today()
        current_month = datetime.now().strftime("%B")

        end_month = today.replace(day=28) + timedelta(days=4)
        end_month = end_month - timedelta(days=end_month.day)
        end_month = datetime.combine(end_month, datetime.min.time()) + timedelta(days=1)

        time_remaining = str(end_month - datetime.now()).split('.')[0]
        return f'{str(current_month)}', time_remaining
    elif timeflag == TimeFlag.WEEK:
        start = get_date_current_week()
        end = start + timedelta(days=6)
        end_week = datetime.combine(end, datetime.min.time()) + timedelta(days=1)
        
        time_remaining = str(end_week - datetime.now()).split('.')[0]
        return f'{start.strftime("%d/%m/%Y")} - {end.strftime("%d/%m/%Y")}', time_remaining
    else:
        tomorrow = datetime.combine(date.today(), datetime.min.time()) + timedelta(days=1)

        time_remaining = str(tomorrow - datetime.now()).split('.')[0]
        return 'Today', time_remaining

def get_datespan_all():
    return date(1000, 1, 1), date(4000, 1, 1)

def get_datespan_month():
    today = date.today()
    start_month = get_date_current_month()
    end_month = today.replace(day=28) + timedelta(days=4)
    end_month = end_month - timedelta(days=end_month.day)
    return start_month, end_month

def get_datespan_day():
    now = datetime.now()
    return date(now.year, now.month, now.day), date(now.year, now.month, now.day)

def get_date_current_week():
    now = date.today()
    return now - timedelta(days=now.weekday())

# Returns 1st of the current month
def get_date_current_month():
    now = datetime.now()
    return date(now.year, now.month, 1)

def get_date_forever_ago():
    return date(1000, 1, 1)