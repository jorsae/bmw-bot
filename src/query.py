from peewee import *
from datetime import datetime, date
import logging

import utility
from enumeration import HallOfFame
from models import *

# Returns the count of a given table
def get_table_count(table):
    return (table
            .select(fn.COUNT())
            .scalar()
            )

# Returns the max value of a given attribute in UserStatModel
def get_max_attribute(attribute):
    return (UserStatModel
                .select(fn.MAX(attribute))
                .scalar()
            )

# Returns sum of attributes, by a user, before and after date
def get_max_day(user_id):
    return (UserStatModel
            .select(
                fn.MAX(UserStatModel.catches).alias("sum_catches"),
                fn.MAX(UserStatModel.legendary).alias("sum_legendary"),
                fn.MAX(UserStatModel.mythical).alias("sum_mythical"),
                fn.MAX(UserStatModel.ultrabeast).alias("sum_ultrabeast"),
                fn.MAX(UserStatModel.shiny).alias("sum_shiny"),
                )
            .where(
                UserStatModel.user_id == user_id
                )
            )

# Returns sum of attribute, by a user
def get_sum(user_id):
    return (UserStatModel
            .select(
                fn.SUM(UserStatModel.catches).alias("sum_catches"),
                fn.SUM(UserStatModel.legendary).alias("sum_legendary"),
                fn.SUM(UserStatModel.mythical).alias("sum_mythical"),
                fn.SUM(UserStatModel.ultrabeast).alias("sum_ultrabeast"),
                fn.SUM(UserStatModel.shiny).alias("sum_shiny"),
                )
            .where(
                UserStatModel.user_id == user_id
                )
            )

# Returns list of all username who matches the max(value) of a certain attribute
def get_username_by_stat(attribute, value):
    users = []
    try:
        subquery = UserStatModel.select(fn.MAX(attribute))
        query = (UserStatModel
                    .select(UserStatModel.user_id)
                    .distinct()
                    .where(attribute == subquery)
                    .order_by(UserStatModel.userstat_id)
                )
        for user in query:
            users.append(get_user_by_userid(user.user_id).username)
        return users
    except Exception as e:
        logging.critical(f'get_username_by_stat: {e}')

# Get UserModel by user_id
def get_user_by_userid(user_id):
    return UserModel.get(UserModel.user_id == user_id)

# Get shiny_hunt by user_id
def get_shinyhunt(discord_id):
    return (UserModel
            .select(UserModel.shiny_hunt)
            .where(UserModel.discord_id == discord_id)
            .scalar()
            )

# Gets amount of people shiny hunting
def get_count_shinyhunt(shiny_hunt):
    return (UserModel
            .select(fn.COUNT())
            .where(UserModel.shiny_hunt == shiny_hunt)
            .scalar())

# Gets MedalList
def get_medallist(amount, page):
    return (MedalModel
            .select()
            .order_by(MedalModel.pokemon_category, MedalModel.value_requirement)
            .limit(amount)
            .paginate(page, amount)
            )

# Gets top most caught pokemon
def get_top_pokemon_catches(amount, page, descending=True):
    order = PokemonModel.catches.desc()
    if descending is False:
        order = PokemonModel.catches
    
    return (PokemonModel
            .select()
            .order_by(order)
            .limit(amount)
            .paginate(page, amount)
            )

# Gets <amount> catches, after <after_date> on page: <page>
def get_top_attribute_desc(attribute, amount, page, after_date):
    return (UserStatModel
            .select(fn.SUM(attribute).alias("sum"), UserStatModel.user_id)
            .where(
                (UserStatModel.date >= after_date) &
                (attribute > 0)
                )
            .group_by(UserStatModel.user_id)
            .order_by(fn.SUM(attribute).desc())
            .limit(amount)
            .paginate(page, amount)
            )

# Adds a pokemon to the rarity definition
def add_rare_definition(pokemon, rarity):
    try:
        pokemon, _ = RareDefinitionModel.get_or_create(pokemon=pokemon, rarity=rarity)
    except Exception as e:
        logging.critical(f'add_rare_definition: {e}')

# Adds a role to the role definition
def add_role_definition(role):
    try:
        role, _ = RoleDefinitionModel.get_or_create(role=role)
    except Exception as e:
        logging.critical(f'add_role_definition: {e}')

# Checks if a role is blacklisted. returns boolean
def role_is_blacklisted(role):
    try:
        query = (RoleDefinitionModel
                    .select()
                    .where(RoleDefinitionModel.role == role)
                )
        return query.exists()
    except Exception as e:
        logging.critical(f'role_is_blacklisted: {e}')

def get_shiny_hunt():
    try:
        query = (UserModel
                    .select()
                    .where(UserModel.shiny_hunt != None)
                    .order_by(UserModel.shiny_hunt)
                )
        return query
    except Exception as e:
        logging.critical(f'get_shiny_hunt: {e}')

# Returns count of all pokemon caught
def get_pokemon_caught(alltime=False):
    try:
        if alltime:
            return UserStatModel.select(fn.SUM(UserStatModel.catches)).scalar()
        else:
            this_month = utility.get_date_current_month()
            return UserStatModel.select(fn.SUM(UserStatModel.catches)).where(UserStatModel.date >= this_month).scalar()
    except Exception as e:
        logging.critical(f'get_pokemon_caught: {e}')
        return 0

def create_user(discord_id, username, shiny_hunt=None):
    try:
        # Ensure User is in database
        user = UserModel.select().where(UserModel.discord_id == discord_id)
        if len(user) <= 0:
            return UserModel.get_or_create(discord_id=discord_id, username=username, shiny_hunt=shiny_hunt)
        else:
            user = user.get()
            return user, None
    except Exception as e:
        logging.critical(f'create_user: {e} | {discord_id}, {shiny_hunt}')