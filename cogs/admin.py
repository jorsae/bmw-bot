import discord
from peewee import *
from datetime import datetime
from discord.ext import commands, flags

import utility
import constants
import query
from UserModel import UserModel
from UserStatModel import UserStatModel
from RareDefinitionModel import RareDefinitionModel
from PokemonModel import PokemonModel
from MedalModel import MedalModel

class Admin(commands.Cog):
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
    
    @commands.command(name='dbstats', help=f'Display table count', hidden=True)
    async def dbstats(self, ctx):
        is_admin = utility.is_admin(ctx.message.author, self.settings.admin)
        if is_admin is False:
            return
        total_users = UserModel.select(fn.COUNT()).scalar()
        total_userstat = UserStatModel.select(fn.COUNT()).scalar()
        total_rares_definition = RareDefinitionModel.select(fn.COUNT()).scalar()
        total_pokemon = PokemonModel.select(fn.COUNT()).scalar()
        total_medals = MedalModel.select(fn.COUNT()).scalar()

        await ctx.send(f'Total users: {total_users}\nTotal UserStat: {total_userstat}\nTotal Rares Defined: {total_rares_definition}\nTotal Pokemon: {total_pokemon}\nTotal Medals: {total_medals}')
    
    @commands.command(name='guild', help='Displays guilds', hidden=True)
    async def guild(self, ctx):
        is_admin = utility.is_admin(ctx.message.author, ['Rither#7897'])
        if is_admin is False:
            return
        
        guild_names = f'{datetime.now()}\n'
        for guild in self.bot.guilds:
            guild_names += f'{guild.name}\n'
        await ctx.author.send(guild_names)

    @commands.command(name='addmedal', help=f'Adds a medal to MedalList.\nUsage: `{constants.CURRENT_PREFIX}addmedal description pokemon_category value_requirement time_category medal`', hidden=True)
    async def addmedal(self, ctx, description, pokemon_category, value_requirement, time_category, medal):
        is_admin = utility.is_admin(ctx.message.author, ['Rither#7897'])
        if is_admin is False:
            return
        
        new_medal, created = MedalModel.get_or_create(description=description, pokemon_category=pokemon_category, value_requirement=value_requirement, time_category=time_category, medal=medal)
        await ctx.send(f'New medal, created: {created}')

    @commands.command(name='delmedal', help=f'Deletes a medal: `{constants.CURRENT_PREFIX}delmedal <medal_id>`', hidden=True)
    async def delmedal(self, ctx, medal_id):
        is_admin = utility.is_admin(ctx.message.author, ['Rither#7897'])
        if is_admin is False:
            return
        
        if medal_id is None:
            await ctx.send('medal_id is None')
        deleted = MedalModel.delete().where(MedalModel.medal_id == medal_id).execute()
        await ctx.send(f'Deleted: {deleted} MedalModels')

    @commands.command(name='dumpmedal', help=f'Displays medals', hidden=True)
    async def dumpmedal(self, ctx):
        is_admin = utility.is_admin(ctx.message.author, ['Rither#7897'])
        if is_admin is False:
            return
        query = (MedalModel
                .select()
                .order_by(MedalModel.pokemon_category))
        output = ''
        for medal in query:
            output += f'[{medal.medal_id}] {medal.description}: {medal.pokemon_category}, {medal.time_category}\n'
        await ctx.send(output)

    @commands.command(name='sync', help=f'Check sync', hidden=True)
    async def sync(self, ctx):
        is_admin = utility.is_admin(ctx.message.author, ['Rither#7897'])
        if is_admin is False:
            return

        total_caught = query.get_pokemon_caught(alltime=True)
        await ctx.send(f'before parse: {self.settings.total_pokemon_before_parse}\ndb: {total_caught}\nafter parse: {self.settings.total_pokemon_after_parse}')

    @commands.command(name='speak', help=f'Make me speak.\nUsage: `{constants.CURRENT_PREFIX}speak <channel_id> "<message>"`', hidden=True)
    async def speak(self, ctx, channel_id, message):
        is_admin = utility.is_admin(ctx.message.author, ['Rither#7897'])
        if is_admin is False:
            return
        try:
            channel_id = int(channel_id)
            channel = self.bot.get_channel(channel_id)
            await channel.send(message)
        except:
            pass