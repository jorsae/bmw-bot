import discord
from peewee import *
from datetime import datetime
from discord.ext import commands, flags

from UserModel import UserModel
from UserStatModel import UserStatModel
from RareDefinitionModel import RareDefinitionModel
from PokemonModel import PokemonModel

class Admin(commands.Cog):
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
    
    @commands.command(name='dbstats', help=f'Display table count', hidden=True)
    async def dbstats(self, ctx):
        total_users = UserModel.select(fn.COUNT()).scalar()
        total_userstat = UserStatModel.select(fn.COUNT()).scalar()
        total_rares_definition = RareDefinitionModel.select(fn.COUNT()).scalar()
        total_pokemon = PokemonModel.select(fn.COUNT()).scalar()

        await ctx.send(f'Total users: {total_users}\nTotal UserStat: {total_userstat}\nTotal Rares Defined: {total_rares_definition}\nTotal Pokemon: {total_pokemon}')
    
    @commands.command(name='speak', help=f'Make me speak.\nUsage: `.speak <channel_id> "<message>"`', hidden=True)
    async def speak(self, ctx, channel_id, message):
        try:
            channel_id = int(channel_id)
            channel = self.bot.get_channel(channel_id)
            await channel.send(message)
        except:
            pass