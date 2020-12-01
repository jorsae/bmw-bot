import discord
import math
import asyncio
import os
import re
import logging
import schedule
from datetime import datetime, timedelta
from discord.ext import commands as discord_commands
from discord.ext import tasks

import query
import RankRewards
import constants
from poketwo import Poketwo
import utility
from models import *
from settings import Settings
import cogs

settings = Settings('../settings.json')
bot = discord_commands.Bot(command_prefix=discord_commands.when_mentioned_or(constants.DEFAULT_PREFIX))
bot.remove_command('help')

poketwo = Poketwo(bot, settings)

@bot.event
async def on_guild_join(guild):
    discord_user = await bot.fetch_user(321079228810657793)
    await discord_user.send(f'Joined server: {guild.name}')

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
        logging.info(f'({str(message.author)}) - [{message.guild.name}]#{message.channel.name} Command: "{message.content}"')
    
    if str(message.author) == constants.POKETWO:
        await poketwo.process_message(message)

    await bot.process_commands(message)

def build_rares():
    add_rares(f'{constants.RARE_DEFINITION_FOLDER}/legendary.txt', 'legendary')
    add_rares(f'{constants.RARE_DEFINITION_FOLDER}/mythical.txt', 'mythical')
    add_rares(f'{constants.RARE_DEFINITION_FOLDER}/ultrabeast.txt', 'ultra beast')

def add_rares(file, rarity):
    for line in open(file, 'r').readlines():
        line = line.strip()
        query.add_rare_definition(line, rarity)

@tasks.loop(seconds=120, reconnect=True)
async def change_status():
    total_caught = query.get_pokemon_caught(alltime=True)
    total_caught = 0 if total_caught is None else total_caught
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{total_caught:,} caught'))

@tasks.loop(seconds=50, reconnect=True)
async def check_rank_rewards():
    # schedule.run_pending()
    schedule.run_all()

@bot.event
async def on_ready():
    change_status.start()
    check_rank_rewards.start()

def setup_logging():
    logFolder = '../logs'
    logFile = 'BMW.log'
    if not os.path.isdir(logFolder):
        os.makedirs(logFolder)
    handler = logging.FileHandler(filename=f'{logFolder}/{logFile}', encoding='utf-8', mode='a+')
    logging.basicConfig(handlers=[handler], level=logging.INFO, format='%(asctime)s %(levelname)s:[%(filename)s:%(lineno)d] %(message)s')

def setup_database():
    database.create_tables([UserModel, PokemonModel, RareDefinitionModel, UserStatModel, MedalModel, RankModel])

if __name__ == '__main__':
    setup_logging()
    setup_database()
    settings.parse_settings()
    bot.command_prefix = discord_commands.when_mentioned_or(settings.prefix)
    constants.CURRENT_PREFIX = settings.prefix # Way to have prefix in command.help description
    build_rares()
    
    schedule.every().day.at("11:31").do(RankRewards.give_rewards) # Schedule to run to automatically distribute weekly/monthly rewards
    
    bot.add_cog(cogs.Ranking(bot, settings))
    bot.add_cog(cogs.General(bot, settings))
    bot.add_cog(cogs.Admin(bot, settings))

    bot.run(settings.token)