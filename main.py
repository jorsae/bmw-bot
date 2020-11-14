import discord
import math
import asyncio
import os
import re
import logging
from datetime import datetime, timedelta
from discord.ext import commands as discord_commands

import constants
from BaseModel import BaseModel, database
from UserModel import UserModel
from PokemonModel import PokemonModel
from settings import Settings

settings = Settings('settings.json')
bot = discord_commands.Bot(command_prefix=constants.PREFIX)
bot.remove_command('help')

@bot.command(name="test", hidden=True)
async def test(ctx):
    channel = bot.get_channel(777055535228911666)
    await ctx.send("test")

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
        print(f'[{str(message.author)=}]: {message.content=}')
        await process_poketwo(message)

    await bot.process_commands(message)

async def process_poketwo(message):
    if 'You caught a level' in message.content:
        pokemon = constants.GET_POKEMON.search(message.content)
        user = get_from_message(constants.GET_USER, message.content)
        user = user[2:]
        print(f'{user=}')
        pokemon = get_from_message(constants.GET_POKEMON, message.content)
        pokemon = pokemon[2:len(pokemon) - 1]
        print(f'{pokemon=}')
        channel = bot.get_channel(777055535228911666)
        await channel.send(f'{bot.get_user(int(user)).name} caught: {pokemon}')

def get_from_message(regex, content):
        get = regex.search(content)
        if get:
            get = get.group(0)
            return get
        else:
            logging.warning(f'Failed to get: {content}')
            return None

def setup_database():
    database.create_tables([UserModel, PokemonModel])

def setup_logging():
    logFolder = 'logs'
    logFile = 'BMW.log'
    if not os.path.isdir(logFolder):
        os.makedirs(logFolder)
    
    logging.basicConfig(filename=f'{logFolder}/{logFile}', level=logging.INFO, format='%(asctime)s %(levelname)s:[%(filename)s:%(lineno)d] %(message)s')
        
if __name__ == '__main__':
    setup_logging()
    setup_database()
    settings.parse_settings()
    bot.run(settings.token)