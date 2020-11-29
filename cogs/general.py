import discord
from peewee import *
from discord.ext import commands, flags
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
from models import PokemonModel, MedalModel, UserStatModel

class General(commands.Cog):
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
    
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
    
    @flags.add_flag('--desc', action='store_true', default=True)
    @flags.add_flag('--asc', action='store_true', default=False)
    @flags.add_flag("pokemon", nargs="*", type=str, default=None)
    @flags.command(name="catch", aliases=['c'], help=f'Displays times a pokémon has been caught.\n`Usage: {constants.CURRENT_PREFIX}catch <pokemon name> [Flags]`\nFlags: `--desc, --asc`')
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
                time = 'time' if pokemon.catches <= 1 else 'times'
                await ctx.send(f'**{string.capwords(pokemon.pokemon)}** has been caught {pokemon.catches:,} {time}!')
            except DoesNotExist:
                await ctx.send(f'**{string.capwords(pokemon)}** has yet to be caught!')
            except Exception as e:
                logging.critical(f'general.catch: {e}')
                await ctx.send('Oops, something went wrong')
            return

        descending = False if flags["asc"] else True
        try:
            current_page = 1
            total_pokemon = PokemonModel.select(fn.COUNT()).scalar()
            max_page = math.ceil(total_pokemon / constants.ITEMS_PER_PAGE)
            
            pokemon_catches = query.get_top_pokemon_catches(constants.ITEMS_PER_PAGE, current_page, descending)
            message = await ctx.send(embed=cog_help.catch_embed(pokemon_catches, current_page, max_page, descending))
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
                
                pokemon_catches = query.get_top_pokemon_catches(constants.ITEMS_PER_PAGE, current_page, descending)
                await message.edit(embed=cog_help.catch_embed(pokemon_catches, current_page, max_page, descending))
                await message.remove_reaction(reaction, user)
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            logging.critical(f'general.catch: {e}')
            embed = discord.Embed(colour=constants.COLOUR_ERROR, title=f'Oops, something went wrong')
            await ctx.send(embed=embed)

    @commands.command(name='check', help=f'Check who/how many people have a medal.\nUsage: `{constants.CURRENT_PREFIX}check <medal emote>`.\ne.g: `{constants.CURRENT_PREFIX}check TrioBadge`')
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

    @commands.command(name='guild', help='Displays guilds')
    async def guild(self, ctx):
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
        output = ''
        for guild in self.bot.guilds:
            output += f'{guild.name}\n'
        embed.add_field(name='Servers I am in', value=output)
        await ctx.send(embed=embed)

    @commands.command(name='ping', help="Checks the bot's latency")
    async def ping(self, ctx):
        start = time.monotonic()
        message = await ctx.send('Pong!')
        ping = (time.monotonic() - start) * 1000
        await message.edit(content=f'Pong! {int(ping)} ms')

    @commands.command(name='help', help='Displays this help message')
    async def help(self, ctx):
        author = ctx.message.author
        display_hidden_commands = utility.is_admin(author, self.settings.admin)

        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
        embed.set_author(name=f'BMW Help')
        last_command = None
        for command in self.bot.walk_commands():
            command = self.bot.get_command(str(command))
            if command is None:
                continue
            if command.hidden is False or display_hidden_commands:
                if last_command != str(command):
                    embed.add_field(name=f'{self.settings.prefix}{command}', value=command.help, inline=False)
                last_command = str(command)
        await ctx.send(embed=embed)