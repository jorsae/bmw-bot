import discord
from peewee import *
from datetime import datetime, date, timedelta
from discord.ext import commands, flags

import utility
import constants
import query
from models import *

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

        start_date = date(2020, 11, 16)
        now = datetime.now()
        days = (date(now.year, now.month, now.day) - start_date).days
        
        await ctx.send(f'Days running: {days}\nTotal users: {total_users}\nTotal UserStat: {total_userstat}\nTotal Rares Defined: {total_rares_definition}\nTotal Pokemon: {total_pokemon}\nTotal Medals: {total_medals}\n')
    
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
            output += f'[{medal.medal_id}] {medal.description}: {medal.pokemon_category}, {medal.value_requirement}, {medal.time_category}\n'
        await ctx.send(output)
    
    @flags.add_flag("--week", action='store_true', default=True)
    @flags.add_flag("--month", action='store_true', default=True)
    @flags.command(name='dumpreward', help=f'Dumps RankReward rewards.\nFlags: `--week, --month`', hidden=True)
    async def dumpreward(self, ctx, **flags):
        is_admin = utility.is_admin(ctx.message.author, ['Rither#7897'])
        if is_admin is False:
            return
        reward_type = 'week'
        if flags['month']:
            reward_type = 'month'

        rank_rewards = (RankRewardModel
                        .select()
                        .where(RankRewardModel.reward_type == reward_type)
                        )
        output = f'Dumping: {reward_type}\n'
        for rank_reward in rank_rewards:
            output += f'{rank_reward.start_date}: {rank_reward.reward_type} | 1. {rank_reward.place_1}, 2. {rank_reward.place_2}, 3. {rank_reward.place_3}'
        await ctx.send(output)
    
    @flags.add_flag("--start", type=str)
    @flags.add_flag("--1", type=str)
    @flags.add_flag("--2", type=str)
    @flags.add_flag("--3", type=str)
    @flags.add_flag("--publish", action="store_true", default=False)
    @flags.add_flag("--week", action="store_true", default=True)
    @flags.add_flag("--month", action="store_true", default=False)
    @flags.command(name='addreward', help=f'Adds rewards for weekly/monthly catches.\nUsage`{constants.CURRENT_PREFIX}addreward --start <yyyy-mm-dd> --1 <1st emote> --2 <2nd emote> --3 <3r emote>`\nFlags: `--week, --month, --publish`', hidden=True)
    async def week(self, ctx, **flags):
        is_admin = utility.is_admin(ctx.message.author, self.settings.admin)
        if is_admin is False:
            return
        
        start = utility.parse_start_flag(**flags)
        if start is None:
            await ctx.send('You need to set start properly')
            return
        
        rewards = utility.parse_rank_rewards(**flags)
        if None in rewards:
            await ctx.send('You need to set all rewards')
            return

        reward_time = 'week'
        if flags['month']:
            reward_time = 'month'

        if flags["publish"]:
            rank_reward, created = (RankRewardModel
                    .get_or_create(
                        start_date=start,
                        reward_type=reward_time,
                        place_1=rewards[0],
                        place_2=rewards[1],
                        place_3=rewards[2]
                        )
                )
            await ctx.send(f'PUBLISHED: {created}')
        else:
            output = f'start_date: {start}\nreward_type: {reward_time}\nRewards: '
            rank = 1
            for reward in rewards:
                output += f'{rank}. {reward} , '
                rank += 1
            await ctx.send(f'{output}\nNOT PUBLISHED.\nAdd `--publish` to publish')

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