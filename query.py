from peewee import *
from datetime import datetime, date
import logging

import utility
from enumeration import HallOfFame
from UserModel import UserModel
from PokemonModel import PokemonModel
from RareDefinitionModel import RareDefinitionModel
from UserStatModel import UserStatModel
from MedalModel import MedalModel

async def add_pokemon(bot, discord_id, rarity, is_shiny):
    today = datetime.now().date()
    try:
        # Ensure User is in database
        discord_user = await bot.fetch_user(discord_id)
        user_id = UserModel.select(UserModel.user_id).where(UserModel.discord_id == discord_id).scalar()
        if user_id is None:
            username = f'{discord_user.name}#{discord_user.discriminator}'
            user, created = UserModel.get_or_create(discord_id=discord_id, username=username)
            user_id = user.user_id

        # Ensure UserStatModel object exist for user today
        userstat, created = UserStatModel.get_or_create(date=today, user_id=user_id)
        
        # Check if we need to add rarity or shiny
        legendary_count, mythical_count, ultrabeast_count = 0, 0, 0
        if rarity is not None:
            if rarity.rarity == 'legendary':
                legendary_count = 1
            elif rarity.rarity == 'mythical':
                mythical_count = 1
            elif rarity.rarity == 'ultra beast':
                ultrabeast_count = 1
        shiny_count = 1 if is_shiny else 0

        UserStatModel.update(catches=UserStatModel.catches + 1, legendary=UserStatModel.legendary + legendary_count, 
                            mythical=UserStatModel.mythical + mythical_count,
                            ultrabeast=UserStatModel.ultrabeast + ultrabeast_count,
                            shiny=UserStatModel.shiny + shiny_count).where(
                                (UserStatModel.user_id == user_id) &
                                (UserStatModel.date == today)
                            ).execute()
    except Exception as e:
        logging.critical(f'add_pokemon: {e} | discord_id: {discord_id}, rarity: {rarity}, is_shiny: {is_shiny}')

def add_pokemon_catch(pokemon):
    try:
        pokemon, _ = PokemonModel.get_or_create(pokemon=pokemon)
        PokemonModel.update(catches=PokemonModel.catches + 1).where(PokemonModel.pokemon == pokemon).execute()
    except Exception as e:
        logging.critical(f'add_pokemon_catch: {e}')

async def add_user_catch(bot, user_id):
    try:
        query = UserModel.select().where(UserModel.user_id == user_id)
        if query.exists():
            UserModel.update(catches=UserModel.catches + 1).where(UserModel.user_id == user_id).execute()
        else:
            discord_user = await bot.fetch_user(user_id)
            user, _ = UserModel.get_or_create(user_id=user_id, username=f'{discord_user.name}#{discord_user.discriminator}')
            UserModel.update(catches=UserModel.catches + 1).where(UserModel.user_id == user_id).execute()
            logging.info(f'add_user_catch: Added user: {discord_user.name}#{discord_user.discriminator} | ({user_id})')
    except Exception as e:
        logging.critical(f'add_user_catch: {e} | {user_id}')

# Returns the max value of a given attribute in UserStatModel
def get_max_attribute(attribute):
    return (UserStatModel
                .select(fn.MAX(attribute))
                .scalar()
            )

# TODO: Move this to utility or somewhere. query should only have pure database queries
def get_hof_medals(username):
    medals = []

    catches = get_max_attribute(UserStatModel.catches)
    catches_users = get_username_by_stat(UserStatModel.catches, catches)
    if username in catches_users:
        medals.append(HallOfFame.catches)
    
    legendary = get_max_attribute(UserStatModel.legendary)
    legendary_users = get_username_by_stat(UserStatModel.legendary, legendary)
    if username in legendary_users:
        medals.append(HallOfFame.legendary)

    mythical = get_max_attribute(UserStatModel.mythical)
    mythical_users = get_username_by_stat(UserStatModel.mythical, mythical)
    if username in mythical_users:
        medals.append(HallOfFame.mythical)

    ultrabeast = get_max_attribute(UserStatModel.ultrabeast)
    ultrabeast_users = get_username_by_stat(UserStatModel.ultrabeast, ultrabeast)
    if username in ultrabeast_users:
        medals.append(HallOfFame.ultrabeast)

    shiny = get_max_attribute(UserStatModel.shiny)
    shiny_users = get_username_by_stat(UserStatModel.shiny, shiny)
    if username in shiny_users:
        medals.append(HallOfFame.shiny)
    
    return medals

# Returns sum of attributes, by a user, before and after date
def get_max_day(user_id):
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
            .where(UserStatModel.user_id == user_id))

# Returns list of all username who matches the max(value) of a certain attribute
def get_username_by_stat(attribute, value):
    users = []
    try:
        subquery = UserStatModel.select(fn.MAX(attribute))
        query = (UserStatModel
                .select(UserStatModel.user_id)
                .distinct()
                .where(attribute == subquery)
                .order_by(UserStatModel.userstat_id))
        for user in query:
            users.append(get_user_by_userid(user.user_id).username)
        return users
    except Exception as e:
        logging.critical(f'get_username_by_stat: {e}')

# Get UserModel by user_id
def get_user_by_userid(user_id):
    return UserModel.get(UserModel.user_id == user_id)

# Gets MedalList
def get_medallist(amount, page):
    return (MedalModel
            .select()
            .order_by(MedalModel.pokemon_category)
            .limit(amount)
            ).paginate(page, amount)

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
            .limit(amount)).paginate(page, amount)

# Adds a pokemon to the rarity definition
def add_rare_definition(pokemon, rarity):
    try:
        pokemon, _ = RareDefinitionModel.get_or_create(pokemon=pokemon, rarity=rarity)
    except Exception as e:
        logging.critical(f'add_rare_definition: {e}')

# Gets the rarity description for a given pokemon. e.g: legendary, mythical
def get_rare_definition(pokemon):
    try:
        rarity = RareDefinitionModel.select().where(RareDefinitionModel.pokemon == pokemon).get()
        return rarity
    except DoesNotExist:
        return None
    except Exception as e:
        logging.critical(f'get_rare_definition: {e}')
        return None

# Returns count of all pokemon caught
async def get_pokemon_caught(alltime=False):
    try:
        if alltime:
            return UserStatModel.select(fn.SUM(UserStatModel.catches)).scalar()
        else:
            this_month = utility.get_date_current_month()
            return UserStatModel.select(fn.SUM(UserStatModel.catches)).where(UserStatModel.date >= this_month).scalar()
    except Exception as e:
        logging.critical(f'get_pokemon_caught: {e}')
        return 0