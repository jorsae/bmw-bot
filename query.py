from peewee import *
import logging
from UserModel import UserModel
from PokemonModel import PokemonModel
from RareDefinitionModel import RareDefinitionModel
from RareModel import RareModel

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

def add_rarity(rarity):
    logging.info(f'add_rarity: {rarity}')
    try:
        rare_model, created = RareModel.get_or_create(rare_id=1)
        if rarity == 'legendary':
            RareModel.update(legendary=RareModel.legendary + 1).where(RareModel.rare_id == 1).execute()
        elif rarity == 'mythical':
            RareModel.update(mythical=RareModel.mythical + 1).where(RareModel.rare_id == 1).execute()
        elif rarity == 'ultra beast':
            RareModel.update(ultrabeast=RareModel.ultrabeast + 1).where(RareModel.rare_id == 1).execute()
        elif rarity == 'shiny':
            RareModel.update(shiny=RareModel.shiny + 1).where(RareModel.rare_id == 1).execute()
        else:
            logging.warning(f'add_rarity none matched: {rarity}')
    except Exception as e:
        logging.critical(f'add_rarity: {e}')

async def get_pokemon_caught():
    try:
        return UserModel.select(fn.SUM(UserModel.catches)).scalar()
    except Exception as e:
        logging.critical(f'get_pokemon_caught: {e}')
        return 0