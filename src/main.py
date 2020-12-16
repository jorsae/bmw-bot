import discord
import math
import asyncio
import os
import re
import logging
from datetime import datetime, timedelta
from discord.ext import commands as discord_commands
from discord.ext import tasks
from discord.utils import get

import query
import cog_help
from RankRewards import RankRewards
import constants
from poketwo import Poketwo
import utility
from models import *
from settings import Settings
import cogs

settings = Settings('../settings.json')
intents = discord.Intents.default()
intents.members = True

bot = discord_commands.Bot(command_prefix=discord_commands.when_mentioned_or(constants.DEFAULT_PREFIX), intents=intents)
bot.remove_command('help')

rank_rewards = RankRewards(bot, settings)
poketwo = Poketwo(bot, settings)

@bot.event
async def on_guild_join(guild):
    discord_user = await bot.fetch_user(321079228810657793)
    await discord_user.send(f'Joined server: {guild.name}')

@bot.event
async def on_member_join(member):
    username = f'{member.name}#{member.discriminator}'
    if member.guild.id not in constants.BMW_SERVERS:
        logging.info(f'{username} joined: {member.guild.name} | No need to do anything')
        return
    shiny_hunt = query.get_shinyhunt(member.id)
    if shiny_hunt is None:
        logging.info(f'{username} has no shiny_hunt')
        return

    role = get(member.guild.roles, name=shiny_hunt)
    if role is None:
        role = await member.guild.create_role(name=shiny_hunt, mentionable=True)
        logging.info(f'{username} joined {member.guild.name}. Created role: {shiny_hunt}')
    else:
        logging.info(f'{username} joined {member.guild.name}. Role already exists: {shiny_hunt}')
    await member.add_roles(role)

@bot.event
async def on_member_remove(member):
    username = f'{member.name}#{member.discriminator}'
    if member.guild.id not in constants.BMW_SERVERS:
        logging.info(f'{username} left: {member.guild.name} | No need to do anything')
        return
    
    shiny_hunt = query.get_shinyhunt(member.id)
    if shiny_hunt is None:
        logging.info(f'{username} has no shiny_hunt')
        return
    role = get(member.guild.roles, name=shiny_hunt)
    if role is None:
        logging.info(f'{username} left {member.guild.name}. Role does not exists: {shiny_hunt}')
    else:
        if len(role.members) <= 0:
            logging.info(f'{username} left {member.guild.name}. Deleted role: {shiny_hunt} | members: {len(role.members)}')
            await role.delete()
        else:
            logging.info(f'{username} left {member.guild.name}. Did not delete role: {shiny_hunt} | members: {len(role.members)}')

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

    if str(message.author) != settings.discord_bot:
        await process_on_triggers(message)


async def process_on_triggers(message):
    if 'barrel roll' in message.content:
        await barrel_roll(message)
    
    if message.content.startswith('?afk'):
        await message.channel.send("I took <@155149108183695360>'s job. Use `.afk` instead :)")
    
    if message.content.startswith(f'{constants.DEFAULT_PREFIX}afk'):
        return

    is_afk = query.get_is_afk_by_discordid(message.author.id)
    if is_afk:
        try:
            await message.channel.send(f'Welcome back <@{message.author.id}>')
        except Exception as e:
            logging.info(f"Can't welcome back: {message.author.display_name} | {e}")
        output = await cog_help.update_afk_status(bot, message.author.id, False)

async def barrel_roll(message):
    text = 'barrel roll'
    cd = 0.5
    msg = await message.channel.send('barrel roll')
    await asyncio.sleep(cd)
    await msg.edit(content='\n'.join(text[i:i+1] for i in range(0, len(text))))
    await asyncio.sleep(cd)
    text_rev = text[::-1]
    await msg.edit(content=text_rev)
    await asyncio.sleep(cd)
    await msg.edit(content='\n'.join(text_rev[i:i+1] for i in range(0, len(text_rev))))
    await asyncio.sleep(cd)
    await msg.edit(content=text)

def build_rares():
    add_rares(f'{constants.RARE_DEFINITION_FOLDER}/legendary.txt', 'legendary')
    add_rares(f'{constants.RARE_DEFINITION_FOLDER}/mythical.txt', 'mythical')
    add_rares(f'{constants.RARE_DEFINITION_FOLDER}/ultrabeast.txt', 'ultra beast')
    add_roles(f'{constants.RARE_DEFINITION_FOLDER}/roles.txt')

def add_roles(file):
    for line in open(file, 'r', encoding='utf-8').readlines():
        line = line.strip().lower()
        query.add_role_definition(line)

def add_rares(file, rarity):
    for line in open(file, 'r').readlines():
        line = line.strip()
        query.add_rare_definition(line, rarity)

@tasks.loop(seconds=120, reconnect=True)
async def change_status():
    total_caught = query.get_pokemon_caught(alltime=True)
    total_caught = 0 if total_caught is None else total_caught
    await bot.change_presence(activity=discord.Activity(type=discord.ActivityType.watching, name=f'{total_caught:,} caught'))

@tasks.loop(seconds=60, reconnect=True)
async def check_rank_rewards():
    now = datetime.now()
    if now.hour == 0 and now.minute == 0:
        await rank_rewards.distribute_rewards()

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
    database.create_tables([UserModel, PokemonModel, RareDefinitionModel, UserStatModel, MedalModel, RankModel, RankRewardModel, RoleDefinitionModel])

if __name__ == '__main__':
    setup_logging()
    setup_database()
    settings.parse_settings()
    bot.command_prefix = discord_commands.when_mentioned_or(settings.prefix)
    build_rares()
    
    bot.add_cog(cogs.Ranking(bot, settings))
    bot.add_cog(cogs.General(bot, settings))
    bot.add_cog(cogs.Admin(bot, settings))

    bot.run(settings.token)