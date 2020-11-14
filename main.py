import discord
import math
import asyncio
import os
import re
import logging
from datetime import datetime, timedelta
from discord.ext import commands as discord_commands

import query
import commands
import constants
from BaseModel import BaseModel, database
from UserModel import UserModel
from PokemonModel import PokemonModel
from RareDefinitionModel import RareDefinitionModel
from RareModel import RareModel
from settings import Settings

settings = Settings('settings.json')
bot = discord_commands.Bot(command_prefix=constants.PREFIX)
bot.remove_command('help')

@bot.command(name="leaderboard", help="Displays the leaderboard")
async def leaderboard(ctx):
    leaderboard_response = await commands.leaderboard(ctx, bot)
    await ctx.send(embed=leaderboard_response)

@bot.command(name="profile", help="Displays your profile")
async def profile(ctx):
    profile_response = await commands.profile(ctx, bot)
    await ctx.send(embed=profile_response)

@bot.command(name="catch", help=f'Displays how many times a pokémon has been caught. usage: {constants.PREFIX}catch <pokemon_name>')
async def catch(ctx, pokemon: str):
    catch_response = commands.catch(pokemon)
    await ctx.send(embed=catch_response)

@bot.command(name="rares", help=f'Displays how many rare pokémon have been caught')
async def rares(ctx):
    rares_response = commands.rares()
    await ctx.send(embed=rares_response)

@bot.command(name='help', help='Displays this help message')
async def help(ctx):
    help_embed = commands.help(ctx, settings, bot)
    await ctx.send(embed=help_embed)

@bot.event
async def on_message(message: discord.Message):
    await bot.wait_until_ready()
    message.content = (
        message.content
        .replace("—", "--")
        .replace("'", "′")
        .replace("‘", "′")
        .replace("’", "′")
    )
    
    if message.content.startswith(constants.PREFIX):
        logging.info(f'[{str(message.author)}] Command: "{message.content}"')
    
    if str(message.author) == constants.POKETWO:
        await process_poketwo(message.content)

    await bot.process_commands(message)

async def process_poketwo(content):
    content = content.lower()
    if 'you caught a level' in content:
        user_id, pokemon = get_userid_pokemon(content)
        if user_id is None or pokemon is None:
            logging.critical(f'process_poketwo error: user_id: {user_id}, pokemon: {pokemon}. {content=}')
            return
        
        # Handle rarity count
        rarity = query.get_rare_definition(pokemon)
        handle_rarity_count(rarity)

        # Handle shiny count
        shiny = pokemon_is_shiny(content)
        if shiny:
            query.add_rarity('shiny')
        
        query.add_user_catch(user_id)
        query.add_pokemon_catch(pokemon)
        
        # Temporary logging for debugging
        channel = bot.get_channel(777055535228911666)
        await channel.send(f'{content}\n{bot.get_user(user_id).name} caught: "{pokemon}" Rarity: {rarity}')

def pokemon_is_shiny(content):
    if 'these colors seem unusual..' in content:
        logging.info(f'Found shiny: {content}')
        return True
    else:
        return False

def handle_rarity_count(rarity):
    if rarity is None:
        return
    else:
        query.add_rarity(rarity.rarity)
        logging.info(f'Found rarity: {rarity}')

def get_userid_pokemon(content):
    user = get_from_message(constants.GET_USER, content)
    if user is not None:
        user = int(user[2:])

    pokemon = constants.GET_POKEMON.search(content)
    if '♀️' in content:
        pokemon = 'nidoran:female_sign:'
    elif '♂️' in content:
        pokemon = 'nidoran:male_sign:'
    else:
        pokemon = get_from_message(constants.GET_POKEMON, content)
        if pokemon is not None:
            pokemon = pokemon[2:len(pokemon) - 1]
    return user, pokemon

def get_from_message(regex, content):
    get = regex.search(content)
    if get:
        get = get.group(0)
        return get
    else:
        logging.warning(f'Failed to get: {content}')
        return None

def setup_database():
    database.create_tables([UserModel, PokemonModel, RareDefinitionModel, RareModel])

def build_rares():
    add_rares(f'{constants.RARE_DEFINITION_FOLDER}/legendary.txt', 'legendary')
    add_rares(f'{constants.RARE_DEFINITION_FOLDER}/mythical.txt', 'mythical')
    add_rares(f'{constants.RARE_DEFINITION_FOLDER}/ultrabeast.txt', 'ultra beast')

def add_rares(file, rarity):
    for line in open(file, 'r').readlines():
        line = line.strip()
        query.add_rare_definition(line, rarity)

def setup_logging():
    logFolder = 'logs'
    logFile = 'BMW.log'
    if not os.path.isdir(logFolder):
        os.makedirs(logFolder)
    handler = logging.FileHandler(filename=f'{logFolder}/{logFile}', encoding='utf-8', mode='a+')
    logging.basicConfig(handlers=[handler], level=logging.INFO, format='%(asctime)s %(levelname)s:[%(filename)s:%(lineno)d] %(message)s')

if __name__ == '__main__':
    setup_logging()
    setup_database()
    settings.parse_settings()
    build_rares()
    
    bot.run(settings.token)