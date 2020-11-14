import logging
from UserModel import UserModel
from PokemonModel import PokemonModel

def add_pokemon_catch(pokemon):
    try:
        pokemon, _ = PokemonModel.get_or_create(pokemon=pokemon)
        PokemonModel.update(catches=PokemonModel.catches + 1).where(PokemonModel.pokemon == pokemon).execute()
    except Exception as e:
        logging.critical(f'add_pokemon_catch: {e}')

def add_user_catch(user_id):
    try:
        user, _ = UserModel.get_or_create(user_id=user_id)
        UserModel.update(catches=UserModel.catches + 1).where(UserModel.user_id == user_id).execute()
    except Exception as e:
        logging.critical(f'add_user_catch: {e}')