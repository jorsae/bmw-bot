import logging

import query
from datetime import datetime, date, timedelta
from enumeration import TimeFlag
from titles import HallOfFame

def parse_time_flags(**flags):
    date = get_date_current_month()
    if flags["all"]:
        print('ALLL')
        print(f'{flags["all"]=}')
        return get_date_forever_ago(), TimeFlag.ALL
    if flags["week"]:
        return get_date_current_week(), TimeFlag.WEEK
    if flags["day"]:
        return date.today(), TimeFlag.DAY
    return date, TimeFlag.MONTH

# returns true if the user is an admin. False otherwise
def is_admin(author, admin_list):
    logging.warning(f'is_admin: {author}')
    if type(author) == str:
        return author in admin_list
    else:
        return str(author) in admin_list

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
    
# Converts a string to integer, defaults to 1
def str_to_int(value):
    try:
        return int(value)
    except:
        return 1

def get_title_author_by_timeflag(timeflag):
    print(f'{timeflag=}')
    if timeflag == TimeFlag.ALL:
        return 'All time', 'Infinite'
    elif timeflag == TimeFlag.MONTH:
        today = date.today()
        current_month = datetime.now().strftime("%B")

        end_month = today.replace(day=28) + timedelta(days=4)
        end_month = end_month - timedelta(days=end_month.day)
        end_month = datetime.combine(end_month, datetime.min.time()) + timedelta(days=1)
        print(f'{end_month=}')
        print(f'{type(end_month)=}')

        return f'{str(current_month)}', end_month - datetime.now()
    elif timeflag == TimeFlag.WEEK:
        start = get_date_current_week()
        end = start + timedelta(days=6)
        end_week = datetime.combine(end, datetime.min.time()) + timedelta(days=1)
        return f'{start.strftime("%d/%m/%Y")} - {end.strftime("%d/%m/%Y")}', end_week - datetime.now()
    else:
        tomorrow = datetime.combine(date.today(), datetime.min.time()) + timedelta(days=1)
        return 'Today', tomorrow - datetime.now()

def get_date_current_week():
    now = date.today()
    return now - timedelta(days=now.weekday())

# Returns 1st of the current month
def get_date_current_month():
    now = datetime.now()
    return date(now.year, now.month, 1)

def get_date_forever_ago():
    return date(1000, 1, 1)