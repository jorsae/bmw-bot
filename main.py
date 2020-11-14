import discord
import math
import asyncio
import os
import logging
from datetime import datetime, timedelta
from discord.ext import commands as discord_commands

from BaseModel import BaseModel, database
import constants
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

    await bot.process_commands(message)

def setup_database():
    database.create_tables([UserModel])

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