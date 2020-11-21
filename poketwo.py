import discord
import logging
from datetime import datetime

import constants
import query
from settings import Settings
from UserModel import UserModel
from UserStatModel import UserStatModel

class Poketwo():
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings

    async def process_message(self, message):
        if message.content is None:
            return
        
        content = message.content.lower()
        if 'you caught a level' in content:
            discord_id, pokemon = self.get_discordid_pokemon(content)
            if discord_id is None or pokemon is None:
                logging.critical(f'poketwo.process_message: discord_id: {discord_id}, pokemon: {pokemon}. {content}')
                return
            
            # Handle rarity count
            rarity = query.get_rare_definition(pokemon)

            # Handle shiny count
            is_shiny = self.pokemon_is_shiny(content)
            if rarity is not None or is_shiny:
                logging.info(f'Found rares/shiny: [{rarity}] - {pokemon}: {content}')

            await self.add_pokemon(discord_id, rarity, is_shiny)
            query.add_pokemon_catch(pokemon)

    async def add_pokemon(self, discord_id, rarity, is_shiny):
        today = datetime.now().date()
        try:
            # Ensure User is in database
            discord_user = await self.bot.fetch_user(discord_id)
            user_id = UserModel.select(UserModel.user_id).where(UserModel.discord_id == discord_id).scalar()
            if user_id is None:
                username = f'{discord_user.name}#{discord_user.discriminator}'
                user, created = UserModel.get_or_create(discord_id=discord_id, username=username)
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

            UserStatModel.update(catches=UserStatModel.catches + 1, legendary=UserStatModel.legendary + legendary_count, 
                                mythical=UserStatModel.mythical + mythical_count,
                                ultrabeast=UserStatModel.ultrabeast + ultrabeast_count,
                                shiny=UserStatModel.shiny + shiny_count).where(
                                    (UserStatModel.user_id == user_id) &
                                    (UserStatModel.date == today)
                                ).execute()
        except Exception as e:
            logging.critical(f'add_pokemon: {e} | discord_id: {discord_id}, rarity: {rarity}, is_shiny: {is_shiny}')

    def get_discordid_pokemon(self, content):
        user = self.get_from_message(constants.GET_USER, content)
        if user is not None:
            user = self.get_from_message(constants.GET_ALL_NUMBERS, user)

        pokemon = constants.GET_POKEMON.search(content)
        if '♀️' in content:
            pokemon = 'nidoran-f'
        elif '♂️' in content:
            pokemon = 'nidoran-m'
        else:
            pokemon = self.get_from_message(constants.GET_POKEMON, content)
            if pokemon is not None:
                pokemon = pokemon[2:len(pokemon) - 1]
        return user, pokemon


    def pokemon_is_shiny(self, content):
        if 'these colors seem unusual..' in content:
            logging.info(f'Found shiny: {content}')
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