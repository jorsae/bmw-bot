import discord
import logging
from datetime import datetime

import constants
import query
from settings import Settings
from models import UserModel, UserStatModel, RareDefinitionModel, PokemonModel

class Poketwo():
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings

    async def process_message(self, message):
        if message.content is None:
            return
        
        content = message.content.lower()
        if 'you caught a level' in content:
            discord_user, pokemon = await self.get_discorduser_pokemon(content)
            if discord_user is None or pokemon is None:
                logging.critical(f'poketwo.process_message: discord_id: {discord_user}, pokemon: {pokemon}. {content}')
                return
            
            # Handle rarity count
            rarity = self.get_rare_definition(pokemon)

            # Handle shiny count
            is_shiny = self.pokemon_is_shiny(content)
            if rarity is not None or is_shiny:
                logging.info(f'[{message.guild.name}]#{message.channel.name} - [{discord_user.name}#{discord_user.discriminator}]: found rares/shiny: ({rarity} / {pokemon}): {content}')

            await self.add_pokemon(discord_user, rarity, is_shiny)
            self.add_pokemon_catch(pokemon)

    async def add_pokemon(self, discord_user, rarity, is_shiny):
        today = datetime.now().date()
        try:
            # Ensure User is in database
            user_id = UserModel.select(UserModel.user_id).where(UserModel.discord_id == discord_user.id).scalar()
            if user_id is None:
                username = f'{discord_user.name}#{discord_user.discriminator}'
                user, created = UserModel.get_or_create(discord_id=discord_user.id, username=username)
                user_id = user.user_id

            # Ensure UserStatModel object exist for user today
            userstat, created = UserStatModel.get_or_create(date=today, user_id=user_id)
            
            # Check if we need to add rarity or shiny
            legendary_count, mythical_count, ultrabeast_count = 0, 0, 0
            if rarity == 'legendary':
                legendary_count = 1
            elif rarity == 'mythical':
                mythical_count = 1
            elif rarity == 'ultra beast':
                ultrabeast_count = 1
            shiny_count = 1 if is_shiny else 0

            (UserStatModel
                .update(
                    catches=UserStatModel.catches + 1,
                    legendary=UserStatModel.legendary + legendary_count, 
                    mythical=UserStatModel.mythical + mythical_count,
                    ultrabeast=UserStatModel.ultrabeast + ultrabeast_count,
                    shiny=UserStatModel.shiny + shiny_count)
                .where(
                    (UserStatModel.user_id == user_id) &
                    (UserStatModel.date == today)
                    )
                .execute()
            )
        except Exception as e:
            logging.critical(f'add_pokemon: {e} | discord_id: {discord_id}, rarity: {rarity}, is_shiny: {is_shiny}')

    def add_pokemon_catch(self, pokemon):
        try:
            pokemon, _ = PokemonModel.get_or_create(pokemon=pokemon)
            (PokemonModel
                .update(
                    catches=PokemonModel.catches + 1
                    )
                .where(
                    PokemonModel.pokemon == pokemon
                    )
                .execute()
            )
        except Exception as e:1
            logging.critical(f'add_pokemon_catch: {e}')

    # Gets the rarity description for a given pokemon. e.g: legendary, mythical
    def get_rare_definition(self, pokemon):
        try:
            rarity = RareDefinitionModel.select(RareDefinitionModel.rarity).where(RareDefinitionModel.pokemon == pokemon).scalar()
            return rarity
        except DoesNotExist:
            return None
        except Exception as e:
            logging.critical(f'get_rare_definition: {e}')
            return None

    async def get_discorduser_pokemon(self, content):
        try:
            # Getting user
            user_id = self.get_from_message(constants.GET_USER, content)
            if user_id is not None:
                user_id = self.get_from_message(constants.GET_ALL_NUMBERS, user_id)
            discord_user = await self.bot.fetch_user(user_id)

            # Getting pokemon
            pokemon = constants.GET_POKEMON.search(content)
            if '♀️' in content:
                pokemon = 'nidoran-f'
            elif '♂️' in content:
                pokemon = 'nidoran-m'
            else:
                pokemon = self.get_from_message(constants.GET_POKEMON, content)
                if pokemon is not None:
                    pokemon = pokemon[2:len(pokemon) - 1]
            
            return discord_user, pokemon
        except Exception as e:
            logging.critical(f'poketwo.get_user_pokemon: {e}')
            return None, None
    
    def pokemon_is_shiny(self, content):
        if 'these colors seem unusual..' in content:
            return True
        else:
            return False

    def get_from_message(self, regex, content):
        get = regex.search(content)
        if get:
            get = get.group(0)
            return get
        else:
            logging.warning(f'Failed to get: {content}')
            return None