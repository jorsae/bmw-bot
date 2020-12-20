import discord
import asyncio
import logging
from peewee import *
from datetime import datetime, date, timedelta
from discord.ext import commands, flags

import utility
import constants
import query
import profile
import cog_help
from RankRewards import RankRewards
from models import *

class Admin(commands.Cog):
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
    
    def is_admin():
        def predicate(ctx):
            return ctx.message.author.id in constants.ADMIN_LIST
        return commands.check(predicate)
    
    def is_moderator():
        def predicate(ctx):
            is_admin = ctx.message.author.id in constants.ADMIN_LIST
            if is_admin:
                return True
            return ctx.message.author.id in constants.MODERATOR_LIST
        return commands.check(predicate)

    @commands.command(name='dbstats', help=f'Display table count')
    @is_moderator()
    async def dbstats(self, ctx):
        total_users = UserModel.select(fn.COUNT()).scalar()
        total_userstat = UserStatModel.select(fn.COUNT()).scalar()
        total_rares_definition = RareDefinitionModel.select(fn.COUNT()).scalar()
        total_pokemon = PokemonModel.select(fn.COUNT()).scalar()
        total_medals = MedalModel.select(fn.COUNT()).scalar()

        start_date = date(2020, 11, 16)
        now = datetime.now()
        days = (date(now.year, now.month, now.day) - start_date).days
        
        await ctx.send(f'Days running: {days}\nTotal users: {total_users}\nTotal UserStat: {total_userstat}\nTotal Rares Defined: {total_rares_definition}\nTotal Pokemon: {total_pokemon}\nTotal Medals: {total_medals}\n')
    
    @commands.command(name='addmedal', help=f'Adds a medal to MedalList.\nUsage: `{constants.DEFAULT_PREFIX}addmedal description pokemon_category value_requirement time_category medal`')
    @is_admin()
    async def addmedal(self, ctx, description, pokemon_category, value_requirement, time_category, medal):
        new_medal, created = MedalModel.get_or_create(description=description, pokemon_category=pokemon_category, value_requirement=value_requirement, time_category=time_category, medal=medal)
        await ctx.send(f'New medal, created: {created}')

    @commands.command(name='delmedal', help=f'Deletes a medal: `{constants.DEFAULT_PREFIX}delmedal <medal_id>`')
    @is_admin()
    async def delmedal(self, ctx, medal_id):
        if medal_id is None:
            await ctx.send('medal_id is None')
        deleted = MedalModel.delete().where(MedalModel.medal_id == medal_id).execute()
        await ctx.send(f'Deleted: {deleted} MedalModels')

    @commands.command(name='dumpmedal', help=f'Displays medals')
    @is_moderator()
    async def dumpmedal(self, ctx):
        query = (MedalModel
                .select()
                .order_by(MedalModel.pokemon_category))
        output = ''
        for medal in query:
            output += f'[{medal.medal_id}] {medal.description}: {medal.pokemon_category}, {medal.value_requirement}, {medal.time_category}\n'
        await ctx.send(output)
    
    @flags.add_flag("--week", action='store_true', default=True)
    @flags.add_flag("--month", action='store_true', default=False)
    @flags.command(name='dumpreward', aliases=['checkreward'], help=f'Dumps RankReward rewards.\nFlags: `--week, --month`')
    @is_moderator()
    async def dumpreward(self, ctx, **flags):
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
    @flags.command(name='addreward', help=f'Adds rewards for weekly/monthly catches.\nUsage`{constants.DEFAULT_PREFIX}addreward --start <yyyy-mm-dd> --1 <1st emote> --2 <2nd emote> --3 <3r emote>`\nFlags: `--week, --month, --publish`')
    @is_admin()
    async def week(self, ctx, **flags):
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

    @commands.command(name='clearsh', help=f'Sets shiny_hunt to None for a user.`{constants.DEFAULT_PREFIX}clearsh Someone#2321`')
    @is_moderator()
    async def clearsh(self, ctx, username):
        query = (UserModel
                    .update(shiny_hunt=None)
                    .where(
                        UserModel.username == username
                    )
                ).execute()
        channel = self.bot.get_channel(742567116343083019)
        msg = await channel.fetch_message(786032117293383710) #poke-shiny_hunt
        await cog_help.update_shiny_hunt(msg)
        await ctx.send(f'Set shiny_hunt to None for user: {username}')
    
    @flags.add_flag("--week", action="store_true", default=False)
    @flags.add_flag("--month", action="store_true", default=False)
    @flags.add_flag("--start", type=str)
    @flags.command(name='triggerreward', help='Manually trigger reward.')
    @is_admin()
    async def trigger_reward(self, ctx, **flags):
        start_date = utility.parse_start_flag(**flags)
        if start_date is None:
            await ctx.send('start_date is not set')
            return
        
        if flags["week"]:
            await ctx.send('Triggering weekly giveaway')
            rank_rewards = RankRewards(self.bot, self.settings)
            await rank_rewards.give_weekly(start_date)
        
        if flags["month"]:
            await ctx.send('Triggering monthly giveaway')
            rank_rewards = RankRewards(self.bot, self.settings)
            await rank_rewards.give_monthly(start_date)
    
    @commands.command(name='aprofile', help='Displays a users profile.\nUsage: `.aprofile <discord_id>`')
    @is_moderator()
    async def aprofile(self, ctx, user_id, **flags):
        page = 1
        max_page = 3
        try:
            current_page = page
            user = UserModel.get(UserModel.discord_id == user_id)

            embed = profile.get_profile_page(ctx, user, current_page, max_page, **flags)
            
            message = await ctx.send(embed=embed)
            await message.add_reaction("◀️")
            await message.add_reaction("▶️")
            
            def check(reaction, user):
                if reaction.message.id == message.id:
                    return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
                else:
                    return False
            
            while True:
                reaction, discord_user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                if str(reaction.emoji) == "▶️" and current_page < max_page:
                    current_page += 1
                elif str(reaction.emoji) == "◀️" and current_page > 1:
                    current_page -= 1
                
                embed = profile.get_profile_page(ctx, user, current_page, max_page, **flags)
                await message.edit(embed=embed)
                await message.remove_reaction(reaction, discord_user)
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            logging.critical(f'ranking.profile: {e}')
            embed = discord.Embed(colour=constants.COLOUR_ERROR, title=f'Oops, something went wrong')
            await ctx.send(embed=embed)

    @commands.command(name='staff', help=f'Lists all admins and moderators')
    @is_moderator()
    async def staff(self, ctx):
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
        admins = ''
        for admin in constants.ADMIN_LIST:
            admins += f'<@{admin}>\n'
        embed.add_field(name='Admins', value=admins)
        
        mods = ''
        for mod in constants.MODERATOR_LIST:
            mods += f'<@{mod}>\n'
        embed.add_field(name='Moderators', value=mods)
        await ctx.send(embed=embed)
    
    @commands.command(name='speak', help=f'Make me speak.\nUsage: `{constants.DEFAULT_PREFIX}speak <channel_id> "<message>"`')
    @is_admin()
    async def speak(self, ctx, channel_id, message):
        try:
            channel_id = int(channel_id)
            channel = self.bot.get_channel(channel_id)  
            await channel.send(message)
        except:
            pass