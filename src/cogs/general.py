import discord
from peewee import *
from discord.ext import commands, flags
from discord.utils import get
from datetime import datetime
import string
import asyncio
import math
import time
import logging

import utility
import query
import constants
import cog_help
from models import PokemonModel, MedalModel, UserStatModel, UserModel

class General(commands.Cog):
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
        self.record_list = []
    
    @commands.command(name='medal', aliases=['m', 'medals'], help=f'Displays list of all available medals')
    async def medals(self, ctx):
        total_medals_available = query.get_table_count(MedalModel)
        max_page = math.ceil(total_medals_available / constants.ITEMS_PER_PAGE)
        try:
            current_page = 1

            embed = discord.Embed(colour=constants.COLOUR_NEUTRAL, title=f'List of all available medals [{total_medals_available}]')
            embed.set_footer(text=f'Page: {current_page}/{max_page}')
            medalmodel = query.get_medallist(constants.ITEMS_PER_PAGE, current_page)
            medal_number = (current_page - 1) * constants.ITEMS_PER_PAGE + 1
            for medal in medalmodel:
                embed.add_field(name=f'{medal_number}. {medal.description}', value=f'Reward: {medal.medal} | Category: {medal.pokemon_category}', inline=False)
                medal_number += 1

            message = await ctx.send(embed=embed)
            await message.add_reaction("◀️")
            await message.add_reaction("▶️")

            def check(reaction, user):
                if reaction.message.id == message.id:
                    return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
                else:
                    return False
            
            while True:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                if str(reaction.emoji) == "▶️" and current_page < max_page:
                    current_page += 1
                elif str(reaction.emoji) == "◀️" and current_page > 1:
                    current_page -= 1
                
                embed = discord.Embed(colour=constants.COLOUR_NEUTRAL, title=f'List of all available medals [{total_medals_available}]')
                embed.set_footer(text=f'Page: {current_page}/{max_page}')
                medalmodel = query.get_medallist(constants.ITEMS_PER_PAGE, current_page)
                medal_number = (current_page - 1) * constants.ITEMS_PER_PAGE + 1
                for medal in medalmodel:
                    embed.add_field(name=f'{medal_number}. {medal.description}', value=f'Reward: {medal.medal} category: {medal.pokemon_category}', inline=False)
                    medal_number += 1
                
                await message.edit(embed=embed)
                await message.remove_reaction(reaction, user)
            await ctx.send(embed=embed)
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            logging.critical(f'general.medal: {e}')
            embed = discord.Embed(colour=constants.COLOUR_ERROR, title=f'Oops, something went wrong')
            await ctx.send(embed=embed)
    
    @flags.add_flag('--fled', action='store_true', default=False)
    @flags.add_flag('--desc', action='store_true', default=True)
    @flags.add_flag('--asc', action='store_true', default=False)
    @flags.add_flag("pokemon", nargs="*", type=str, default=None)
    @flags.command(name='catch', aliases=['c'], help=f'Displays times a pokémon has been caught.\n`Usage: {constants.DEFAULT_PREFIX}catch <pokemon name> [Flags]`\nFlags: `--desc, --asc`')
    async def catch(self, ctx, **flags):
        pokemon = flags["pokemon"]

        if len(pokemon) > 0:
            pokemon = ' '.join(pokemon).lower()
            
            # Check for easter egg
            if pokemon in constants.CATCH_BMW_EASTER_EGG:
                await ctx.send(f"Wild <@777052225099792386> fled!")
                return
            
            try:
                pokemon = PokemonModel.get(PokemonModel.pokemon == pokemon)
                time_catches = 'time' if pokemon.catches <= 1 else 'times'
                time_fled = 'time' if pokemon.fled == 1 else 'times'
                embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
                embed.add_field(name=f'**{string.capwords(pokemon.pokemon)} stats**', value=f'**Caught: **{pokemon.catches:,} {time_catches}\n**Fled: **{pokemon.fled:,} {time_fled}')
                await ctx.send(embed=embed)
            except DoesNotExist:
                await ctx.send(f'**{string.capwords(pokemon)}** has yet to be caught!')
            except Exception as e:
                logging.critical(f'general.catch: {e}')
                await ctx.send('Oops, something went wrong')
            return

        descending = False if flags["asc"] else True
        order_attribute = PokemonModel.catches
        if flags['fled']:
            order_attribute = PokemonModel.fled
        try:
            current_page = 1
            total_pokemon = PokemonModel.select(fn.COUNT()).scalar()
            max_page = math.ceil(total_pokemon / constants.ITEMS_PER_PAGE)
            
            pokemon_catches = query.get_top_pokemon_catches(order_attribute, constants.ITEMS_PER_PAGE, current_page, descending)
            message = await ctx.send(embed=cog_help.catch_embed(pokemon_catches, current_page, max_page, descending, flags['fled']))
            await message.add_reaction("◀️")
            await message.add_reaction("▶️")

            def check(reaction, user):
                if reaction.message.id == message.id:
                    return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
                else:
                    return False
            
            while True:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                if str(reaction.emoji) == "▶️" and current_page < max_page:
                    current_page += 1
                elif str(reaction.emoji) == "◀️" and current_page > 1:
                    current_page -= 1
                
                pokemon_catches = query.get_top_pokemon_catches(order_attribute, constants.ITEMS_PER_PAGE, current_page, descending)
                await message.edit(embed=cog_help.catch_embed(pokemon_catches, current_page, max_page, descending, flags['fled']))
                await message.remove_reaction(reaction, user)
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            logging.critical(f'general.catch: {e}')
            embed = discord.Embed(colour=constants.COLOUR_ERROR, title=f'Oops, something went wrong')
            await ctx.send(embed=embed)

    @commands.command(name='check', help=f'Check who/how many people have a medal.\nUsage: `{constants.DEFAULT_PREFIX}check <medal emote>`.\ne.g: `{constants.DEFAULT_PREFIX}check TrioBadge`')
    async def test(self, ctx, medal):
        medal_model = MedalModel.select().where(MedalModel.medal.contains(medal))
        if len(medal_model) <= 0:
            await ctx.send('Found no matches')
            return
        value_requirement = medal_model[0].value_requirement
        pokemon_category = medal_model[0].pokemon_category
        time_category = medal_model[0].time_category
        attribute = None
        if pokemon_category == 'catches':
            attribute = UserStatModel.catches
        elif pokemon_category == 'legendary':
            attribute = UserStatModel.legendary
        elif pokemon_category == 'mythical':
            attribute = UserStatModel.mythical
        elif pokemon_category == 'ultrabeast':
            attribute = UserStatModel.ultrabeast
        elif pokemon_category == 'shiny':
            attribute = UserStatModel.shiny
        elif pokemon_category == 'Hall of Fame':
            await ctx.send(f"I don't support HoF medals.\nPlease use `.hof` to check.")
            return
        else:
            await ctx.send(f'Error in pokemon_category: {pokemon_category}')
            return
        start, end = None, None
        if time_category == 'all':
            start, end = utility.get_datespan_all()
            attribute = fn.SUM(attribute)
        elif time_category == 'day':
            attribute = fn.MAX(attribute)
            start, end = utility.get_datespan_day()
        else:
            await ctx.send(f'Error in time_category {time_category}')
            return
        start, end = utility.get_datespan_all()
        users = (UserStatModel
                    .select(attribute.alias("value"), UserStatModel.user_id)
                    .group_by(UserStatModel.user_id)
                    .having(attribute >= value_requirement)
                    .order_by(attribute.desc())
                )
        
        output = ''
        for user in users:
            username = query.get_user_by_userid(user.user_id).username
            output += f'**{username}: **{user.value:,}\n'
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
        embed.add_field(name=f'{medal_model[0].medal} {medal_model[0].description}\n{len(users)} people have the medal', value=output)
        await ctx.send(embed=embed)
    
    @flags.add_flag("shiny_hunt", nargs="*", type=str, default=None)
    @flags.command(name='shrole', aliases=['sh', 'hunt'], help=f'Start shiny hunt, `{constants.DEFAULT_PREFIX}shrole stop` to stop.\nUsage: `{constants.DEFAULT_PREFIX}shrole <pokemon>`')
    async def shiny_hunt(self, ctx, **flags):
        if ctx.guild.id != constants.ORIGINAL_BMW_SERVER:
            await ctx.send('You have to specify shiny hunt in the main BMW server')
            return

        # Make sure user specified a pokemon to shiny hunt
        shiny_hunt = utility.parse_shinyhunt_flag(**flags)
        if shiny_hunt is None:
            await ctx.send(f'Must specify a pokémon. e.g: `{constants.DEFAULT_PREFIX}sh abra`')
            return
        
        # Make sure the user is not already shiny hunting that pokemon
        username = f'{ctx.author.name}#{ctx.author.discriminator}'
        usermodel, created = query.create_user(ctx.author.id, username, shiny_hunt)
        if usermodel.shiny_hunt == shiny_hunt:
            await ctx.send(f'You are already shiny hunting: {shiny_hunt}')
            return
        
        # Make sure the shiny_hunt is not a blacklisted role
        if query.role_is_blacklisted(shiny_hunt):
            await ctx.send(f"You can't shiny hunt: {shiny_hunt}")
            return
        
        level = cog_help.get_level(ctx.author)
        if level is None:
            await ctx.send(f'Error getting your level')
        if level < constants.MINIMUM_LEVEL_SHINY_HUNT:
            await ctx.send('Too low level to shiny hunt. You have to be level 8+')
            return
        
        process_message = await ctx.send('Processing...')

        if shiny_hunt == 'stop':
            shiny_hunt = None
        
        output = f''
        for guild in constants.LOADED_BMW_SERVERS:
            result = await cog_help.fix_new_roles(self.bot, guild, ctx.author.id, shiny_hunt, usermodel.shiny_hunt)
            if result is not None:
                output += result
            else:
                break
        
        (UserModel.update(
            shiny_hunt=shiny_hunt
            )
            .where(
                UserModel.discord_id == ctx.author.id
            )
            .execute()
        )
        if shiny_hunt is not None:
            embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)

            shiny_hunters = query.get_count_shinyhunt(shiny_hunt)
            if shiny_hunters >= 2:
                embed.set_footer(text=f'{shiny_hunters - 1} other person(s) are also shiny hunting {shiny_hunt}')
            output += f'\n**Remember to change shiny hunt for {constants.POKETWO} too!**'
            embed.add_field(name=f'You are now shiny hunting {string.capwords(shiny_hunt)}.', value=output)
            await process_message.edit(content='', embed=embed)
        else:
            await process_message.edit(content='Stopped your shiny hunt')
        
        channel = self.bot.get_channel(742567116343083019)
        msg = await channel.fetch_message(786032117293383710) #poke-shiny_hunt
        await cog_help.update_shiny_hunt(msg)

        # Update #shiny_hunt_update
        if shiny_hunt is None:
            await self.settings.shiny_hunt_log_channel.send(f'{username} stopped shiny hunt.')
        else:
            await self.settings.shiny_hunt_log_channel.send(f'{username} changed shiny hunt to {string.capwords(shiny_hunt)}')
        
    @commands.command(name='guild', help='Displays guilds')
    async def guild(self, ctx):
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
        output = ''
        for guild in self.bot.guilds:
            output += f'{guild.name}\n'
        embed.add_field(name='Servers I am in', value=output)
        await ctx.send(embed=embed)

    @commands.command(name='afk', help='Sets your status to afk')
    async def afk(self, ctx):
        author = ctx.message.author
        total_length = len(author.display_name) + len(constants.AFK_PREFIX)
        if total_length > constants.MAX_NICKNAME_LENGTH:
            await ctx.send(f'Your nickname would be too long, please shorten it!')
            return
        
        is_afk = query.get_is_afk_by_discordid(author.id)
        if is_afk:
            await ctx.send('You are already afk.')
            return

        await ctx.send(f'<@{ctx.message.author.id}> is now afk.')
        output_guilds = await cog_help.update_afk_status(self.bot, author.id, True)
        if len(output_guilds) <= 0:
            return
        output = f'<@{ctx.message.author.id}> Could not set your name in:\n'
        for guild in output_guilds:
            output += f'{guild}\n'
        await ctx.send(f'{output}\n**Your nickname would be too long, please shorten it!**')
    
    @commands.command(name='unafk', help='Force sets your status/name to NOT be afk')
    async def unafk(self, ctx):
        author = ctx.message.author
        msg = await ctx.send(f'<@{ctx.message.author.id}> force removing afk, give me a moment..')
        await cog_help.update_afk_status(self.bot, author.id, False)
        await msg.edit(content=f'<@{ctx.message.author.id}> afk status removed')
    
    @commands.command(name='updateme', help='Automatically updates your discord name for the bot. This is only applicable if you changed it with discord nitro.')
    async def updateme(self, ctx):
        author = ctx.message.author
        username = f'{author.name}#{author.discriminator}'
        updated = query.update_username(author.id, username)
        if updated:
            await ctx.send('Your username was successfully updated')
        else:
            await ctx.send('Error updating your username. Please let Rither know.')

    @commands.command(name='record', help='Records your catches in a timeframe to track your catches/min')
    async def record(self, ctx):
        id = f'{ctx.message.author.id}'
        # TODO: get total catches
        pass

    @commands.command(name='ping', help="Checks the bot's latency")
    async def ping(self, ctx):
        start = time.monotonic()
        message = await ctx.send('Pong!')
        ping = (time.monotonic() - start) * 1000
        await message.edit(content=f'Pong! {int(ping)} ms')

    @commands.command(name='help', help='Displays this help message')
    async def help(self, ctx):
        author = ctx.message.author
        
        cogs = []
        cogs.append(self.bot.get_cog('Ranking'))
        cogs.append(self.bot.get_cog('General'))
        cogs.append(self.bot.get_cog('Admin'))

        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
        embed.set_author(name=f'BMW Help')
        for cog in cogs:
            for command in cog.walk_commands():
                if await command.can_run(ctx):
                    embed.add_field(name=f'{self.settings.prefix}{command}{utility.get_aliases(command.aliases)}', value=command.help, inline=False)
        await ctx.send(embed=embed)