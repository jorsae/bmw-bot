from peewee import *
from datetime import datetime, date
import logging

from UserModel import UserModel
from PokemonModel import PokemonModel
from RareDefinitionModel import RareDefinitionModel
from UserStatModel import UserStatModel

async def add_pokemon(bot, discord_id, rarity, is_shiny):
    today = datetime.now().date()
    try:
        # Ensure User is in database
        discord_user = await bot.fetch_user(discord_id)
        user, _ = UserModel.get_or_create(discord_id=discord_id)

        # Ensure UserStatModel object exist for user today
        userstat, _ = UserStatModel.get_or_create(date=today, user_id=user.user_id)
        
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
                                (UserStatModel.user_id == user.user_id) &
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

def add_rare_definition(pokemon, rarity):
    try:
        pokemon, _ = RareDefinitionModel.get_or_create(pokemon=pokemon, rarity=rarity)
    except Exception as e:
        logging.critical(f'add_rare_definition: {e}')

def get_rare_definition(pokemon):
    try:
        rarity = RareDefinitionModel.select().where(RareDefinitionModel.pokemon == pokemon).get()
        return rarity
    except DoesNotExist:
        return None
    except Exception as e:
        logging.critical(f'get_rare_definition: {e}')
        return None

async def get_pokemon_caught(this_month=True):
    try:
        if this_month:
            now = datetime.now()
            this_month = date(now.year, now.month, 1)
            return UserStatModel.select(fn.SUM(UserStatModel.catches)).where(UserStatModel.date >= this_month).scalar()
        else:
            return UserStatModel.select(fn.SUM(UserStatModel.catches)).scalar()
    except Exception as e:
        logging.critical(f'get_pokemon_caught: {e}')
        return 0