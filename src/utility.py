import logging

import constants
import query
from datetime import datetime, date, timedelta
from enumeration import TimeFlag, HallOfFame
from models import UserStatModel

def parse_shinyhunt_flag(**flags):
    shiny_hunt = None
    if flags['shiny_hunt']:
        return ''.join(flags['shiny_hunt']).lower()
    else:
        return None

def parse_start_flag(**flags):
    try:
        return datetime.strptime(flags["start"], "%Y-%m-%d").date()
    except Exception as e:
        logging.warning(f'Failed to parse start: {e}')
        return None

def parse_rank_rewards(**flags):
    rewards = []
    rewards.append(flags["1"])
    rewards.append(flags["2"])
    rewards.append(flags["3"])
    return rewards

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

def parse_time_flags(default='month', **flags):
    if flags["all"]:
        return get_date_forever_ago(), TimeFlag.ALL
    elif flags["month"]:
        return get_date_current_month(), TimeFlag.MONTH
    elif flags["week"]:
        return get_date_current_week(), TimeFlag.WEEK
    elif flags["day"]:
        return date.today(), TimeFlag.DAY
    else:
        flags[default] = True
        return parse_time_flags(**flags)

def get_aliases(aliases):
    if aliases == []:
        return ''
    else:
        output = ' | ('
        for alias in aliases:
            output += f'{alias}, '
        output = output[:-2]
        return f'{output})'

# Get rank number, by page
def get_rank_by_page(current_page):
    return current_page * constants.ITEMS_PER_PAGE

# Gets all hof medals by username
def get_hof_medals(username):
    medals = []

    catches = query.get_max_attribute(UserStatModel.catches)
    catches_users = query.get_username_by_stat(UserStatModel.catches, catches)
    if username in catches_users:
        medals.append(HallOfFame.catches)
    
    legendary = query.get_max_attribute(UserStatModel.legendary)
    legendary_users = query.get_username_by_stat(UserStatModel.legendary, legendary)
    if username in legendary_users:
        medals.append(HallOfFame.legendary)

    mythical = query.get_max_attribute(UserStatModel.mythical)
    mythical_users = query.get_username_by_stat(UserStatModel.mythical, mythical)
    if username in mythical_users:
        medals.append(HallOfFame.mythical)

    ultrabeast = query.get_max_attribute(UserStatModel.ultrabeast)
    ultrabeast_users = query.get_username_by_stat(UserStatModel.ultrabeast, ultrabeast)
    if username in ultrabeast_users:
        medals.append(HallOfFame.ultrabeast)

    shiny = query.get_max_attribute(UserStatModel.shiny)
    shiny_users = query.get_username_by_stat(UserStatModel.shiny, shiny)
    if username in shiny_users:
        medals.append(HallOfFame.shiny)
    
    return medals

# returns emote for the given HallOfFame title
def get_hof_emote(title):
    if title == HallOfFame.catches:
        return '<:HofCatches:779248403502202901>'
    if title == HallOfFame.legendary:
        return '<:HofLegendary:779249178525564947>'
    if title == HallOfFame.mythical:
        return '<:HofMythical:779248236892258307>'
    if title == HallOfFame.ultrabeast:
        return '<:HofUltrabeast:779247337977413642>'
    if title == HallOfFame.shiny:
        return '<:HofShiny:779250293849587743>'
    
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
    today = date.today()
    return today, today

def get_date_current_week():
    now = date.today()
    return now - timedelta(days=now.weekday())

# Returns 1st of the current month
def get_date_current_month():
    now = datetime.now()
    return date(now.year, now.month, 1)

def get_date_forever_ago():
    return date(1000, 1, 1)