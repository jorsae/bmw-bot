import discord
import math
import asyncio
import os
import re
import logging
from datetime import datetime, timedelta
from discord.ext import commands as discord_commands
from discord.ext import tasks

import query
import commands
import constants
import utility
from BaseModel import BaseModel, database
from UserModel import UserModel
from PokemonModel import PokemonModel
from RareDefinitionModel import RareDefinitionModel
from RareModel import RareModel
from UserStatModel import UserStatModel
from settings import Settings

settings = Settings('../settings.json')
bot = discord_commands.Bot(command_prefix=constants.DEFAULT_PREFIX)
bot.remove_command('help')

@bot.command(name="leaderboard", help="Displays the leaderboard for total catches in BMW")
async def leaderboard(ctx):
    leaderboard_response = await commands.leaderboard(ctx, bot)
    await ctx.send(embed=leaderboard_response)

@bot.command(name="profile", help="Displays your profile")
async def profile(ctx):
    profile_response = await commands.profile(ctx, bot)
    await ctx.send(embed=profile_response)

@bot.command(name="catch", help=f'Displays how many times a pokémon has been caught.\nusage: {settings.prefix}catch <pokemon name>')
async def catch(ctx, pokemon: str=None):
    catch_response = commands.catch(pokemon)
    await ctx.send(catch_response)

@bot.command(name="rares", help=f'Displays how many rare pokémon have been caught')
async def rares(ctx):
    rares_response = commands.rares()
    await ctx.send(embed=rares_response)

@bot.command(name="server", help='Displays pokémon statistics for BMW')
async def server(ctx):
    server_response = await commands.server()
    await ctx.send(embed=server_response)

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
    
    if message.content.startswith(settings.prefix):
        logging.info(f'[{str(message.author)}] Command: "{message.content}"')
    
    if str(message.author) == constants.POKETWO:
        await process_poketwo(bot, message.content)

    await bot.process_commands(message)

async def process_poketwo(bot, content):
    content = content.lower()
    if 'you caught a level' in content:
        discord_id, pokemon = get_discordid_pokemon(content)
        if discord_id is None or pokemon is None:
            logging.critical(f'process_poketwo error: discord_id: {discord_id}, pokemon: {pokemon}. {content}')
            return
        
        # Handle rarity count
        rarity = query.get_rare_definition(pokemon)

        # Handle shiny count
        is_shiny = pokemon_is_shiny(content)
        
        await query.add_pokemon(bot, discord_id, rarity, is_shiny)
        query.add_pokemon_catch(pokemon)

def pokemon_is_shiny(content):
    if 'these colors seem unusual..' in content:
        logging.info(f'Found shiny: {content}')
        return True
    else:
        return False

def get_discordid_pokemon(content):
    user = get_from_message(constants.GET_USER, content)
    if user is not None:
        user = get_from_message(constants.GET_ALL_NUMBERS, user)

    pokemon = constants.GET_POKEMON.search(content)
    if '♀️' in content:
        pokemon = 'nidoran-f'
    elif '♂️' in content:
        pokemon = 'nidoran-m'
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
    database.create_tables([UserModel, PokemonModel, RareDefinitionModel, RareModel, UserStatModel])

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

@tasks.loop(seconds=600, reconnect=True)
async def change_status():
    caught = await query.get_pokemon_caught()
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{caught:,} pokémon caught'))

@bot.event
async def on_ready():
        change_status.start()

if __name__ == '__main__':
    setup_logging()
    setup_database()
    settings.parse_settings()
    bot.command_prefix = settings.prefix
    build_rares()
    
    bot.run(settings.token)