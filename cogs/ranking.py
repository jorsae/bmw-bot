import discord
from peewee import *
from discord.ext import commands, flags
from datetime import datetime, date
import asyncio
import math
import logging

import constants
import utility
import query
import medals
import profile
from models import UserStatModel, UserModel, PokemonModel
from enumeration import TimeFlag, HallOfFame

class Ranking(commands.Cog):
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
    
    @flags.add_flag("--catches", action="store_true", default=True)
    @flags.add_flag("--legendary", action="store_true", default=False)
    @flags.add_flag("--mythical", action="store_true", default=False)
    @flags.add_flag("--ub", action="store_true", default=False)
    @flags.add_flag("--shiny", action="store_true", default=False)
    @flags.add_flag("--week", action="store_true", default=False)
    @flags.add_flag("--day", action="store_true", default=False)
    @flags.add_flag("--month", action="store_true", default=True)
    @flags.add_flag("--all", action="store_true", default=False)
    @flags.add_flag("page", nargs="?", type=str, default=1)
    @flags.command(name="leaderboard", aliases=['l', 'rank'], help=f'Displays the leaderboard for total catches in BMW.\n`Usage: {constants.CURRENT_PREFIX}leaderboard <page> [flags]`\nTime flags: `--all, --month, --week, --day`\nCategory flags: `--catches, --legendary, --mythical, --ub, --shiny`')
    async def leaderboard(self, ctx, **flags):
        page = abs(utility.str_to_int(flags['page']))
        date, time_flag = utility.parse_time_flags(**flags)
        attribute, field_attribute = utility.parse_attribute_flags(**flags)

        total_ranks = (UserStatModel
                        .select()
                        .where(
                            (UserStatModel.date >= date) &
                            (attribute > 0)
                            )
                        .group_by(UserStatModel.user_id)
                        .count()
                        )
        max_page = math.ceil(total_ranks / constants.ITEMS_PER_PAGE)
        
        if page > max_page:
            page = max_page

        try:
            current_page = page

            top_catches = query.get_top_attribute_desc(attribute, constants.ITEMS_PER_PAGE, current_page, date)

            message = await ctx.send(embed=self.create_leaderboard_embed(top_catches, current_page, max_page, time_flag, field_attribute))
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
                top_catches = query.get_top_attribute_desc(attribute, constants.ITEMS_PER_PAGE, current_page, date)
                await message.edit(embed=self.create_leaderboard_embed(top_catches, current_page, max_page, time_flag, field_attribute))
                await message.remove_reaction(reaction, user)
        except asyncio.TimeoutError:
            logging.warning(f'ranking.leaderboard: timeout')
            pass
        except Exception as e:
            logging.critical(f'commands.leaderboard: {e}')
            embed = discord.Embed(colour=constants.COLOUR_ERROR, title=f'Oops, something went wrong')
            await ctx.send(embed=embed)

    def create_leaderboard_embed(self, query, current_page, max_page, time_flag, field_attribute):
        rank = (current_page * constants.ITEMS_PER_PAGE) - constants.ITEMS_PER_PAGE + 1
        top_rank = constants.ITEMS_PER_PAGE if current_page == 1 else f'{(current_page * constants.ITEMS_PER_PAGE) - constants.ITEMS_PER_PAGE + 1} - {current_page * constants.ITEMS_PER_PAGE}'
        
        title, author = utility.get_title_author_by_timeflag(time_flag)
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL, title=f'Top {top_rank} rankings [{str(title)}]')
        embed.set_footer(text=f'Page: {current_page}/{max_page}')
        embed.set_author(name=f'Time remaining: {str(author)}')

        for user_stat in query:
            user = UserModel.get(UserModel.user_id == user_stat.user_id)
            embed.add_field(name=f'{rank}. {user.username}', value=f'{field_attribute}: {user_stat.sum:,}')
            rank += 1
        return embed
    
    @commands.command(name='profile', aliases=['p'], help="Displays your profile")
    async def profile(self, ctx, **flags):
        page = 1
        max_page = 2
        try:
            current_page = page
            embed = profile.get_profile_page(ctx, current_page, **flags)

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
                
                embed = profile.get_profile_page(ctx, current_page, **flags)
                await message.edit(embed=embed)
                await message.remove_reaction(reaction, user)
        except asyncio.TimeoutError:
            logging.warning(f'ranking.leaderboard: timeout')
            pass
        except Exception as e:
            logging.critical(f'commands.leaderboard: {e}')
            embed = discord.Embed(colour=constants.COLOUR_ERROR, title=f'Oops, something went wrong')
            await ctx.send(embed=embed)

    @commands.command(name='server', aliases=['s'], help='Displays pokémon statistics for BMW')
    async def server(self, ctx):
        total_caught = query.get_pokemon_caught()
        try:
            legendary = UserStatModel.select(fn.SUM(UserStatModel.legendary)).scalar()
            mythical = UserStatModel.select(fn.SUM(UserStatModel.mythical)).scalar()
            ultrabeast = UserStatModel.select(fn.SUM(UserStatModel.ultrabeast)).scalar()
            shiny = UserStatModel.select(fn.SUM(UserStatModel.shiny)).scalar()

            total_rares = legendary + mythical + ultrabeast

            embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
            percent_rare = round(100 / total_caught * total_rares, 2)
            percent_shiny = round(100 / total_caught * shiny, 2)
            embed.add_field(name='BMW pokémon stats', value=f'**Total pokémon caught: **{total_caught:,}\n**Total rare pokémon: **{total_rares:,}\n**Percentage rare pokémon: **{percent_rare}%\n**Total shiny pokémon: **{shiny:,}\n**Percentage shiny pokémon: **{percent_shiny}%')
            await ctx.send(embed=embed)
        except DoesNotExist:
            embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
            embed.add_field(name='BMW pokémon stats', value=f'**Total pokémon caught:** {total_caught:,}\n**Total rare pokémon:** 0\n**Percentage rare pokémon:** 0%\n**Total shiny pokémon: **0\n**Percentage shiny pokémon **0%')
            await ctx.send(embed=embed)
        except Exception as e:
            logging.critical(f'server: {e}')
            embed = discord.Embed(colour=constants.COLOUR_ERROR, title=f'Oops, something went wrong')
            await ctx.send(embed=embed)

    @commands.command(name='rares', aliases=['r'], help=f'Displays how many rare pokémon have been caught')
    async def rares(self, ctx):
        try:
            legendary = UserStatModel.select(fn.SUM(UserStatModel.legendary)).scalar()
            mythical = UserStatModel.select(fn.SUM(UserStatModel.mythical)).scalar()
            ultrabeast = UserStatModel.select(fn.SUM(UserStatModel.ultrabeast)).scalar()
            shiny = UserStatModel.select(fn.SUM(UserStatModel.shiny)).scalar()

            total_rares = legendary + mythical + ultrabeast
            embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
            embed.add_field(name='Rare pokémon caught', value=f'**Total: **{total_rares:,}\n**Legendary: **{legendary:,}\n**Mythical: **{mythical:,}\n**Ultra beast: **{ultrabeast:,}\n**Shiny: **{shiny:,}')
            await ctx.send(embed=embed)
        except DoesNotExist:
            embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
            embed.add_field(name='Rare pokémon caught', value=f'**Total:** 0\n**Legendary**: 0\n**Mythical**: 0\n**Ultra beast**: 0\n**Shiny**: 0')
            await ctx.send(embed=embed)
        except Exception as e:
            logging.critical(f'commands.catch: {e}')
            embed = discord.Embed(colour=constants.COLOUR_ERROR, title=f'Oops, something went wrong')
            await ctx.send(embed=embed)
        
    @commands.command(name='hof', help=f'Hall of fame!')
    async def hof(self, ctx):
        try:
            embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
            embed.add_field(name='Hall of Fame [daily records]', value=f'For achieving the highest amount of catches in a single day\nThe medals will be displayed in your `{constants.CURRENT_PREFIX}profile`')
            
            catches = query.get_max_attribute(UserStatModel.catches)
            catches_users = "\n".join(query.get_username_by_stat(UserStatModel.catches, catches))

            legendary = query.get_max_attribute(UserStatModel.legendary)
            legendary_users = "\n".join(query.get_username_by_stat(UserStatModel.legendary, legendary))

            mythical = query.get_max_attribute(UserStatModel.mythical)
            mythical_users = "\n".join(query.get_username_by_stat(UserStatModel.mythical, mythical))

            ultrabeast = query.get_max_attribute(UserStatModel.ultrabeast)
            ultrabeast_users = "\n".join(query.get_username_by_stat(UserStatModel.ultrabeast, ultrabeast))

            shiny = query.get_max_attribute(UserStatModel.shiny)
            shiny_users = "\n".join(query.get_username_by_stat(UserStatModel.shiny, shiny))

            embed.add_field(name=f'{utility.get_hof_emote(HallOfFame.catches)} All pokémon: {catches:,}', value=f'{catches_users}', inline=False)
            embed.add_field(name=f'{utility.get_hof_emote(HallOfFame.legendary)} Legendary: {legendary}', value=f'{legendary_users}', inline=False)
            embed.add_field(name=f'{utility.get_hof_emote(HallOfFame.mythical)} Mythical: {mythical}', value=f'{mythical_users}', inline=False)
            embed.add_field(name=f'{utility.get_hof_emote(HallOfFame.ultrabeast)} Ultra Beast: {ultrabeast}', value=f'{ultrabeast_users}', inline=False)
            embed.add_field(name=f'{utility.get_hof_emote(HallOfFame.shiny)} Shiny: {shiny}', value=f'{shiny_users}', inline=False)
            
            await ctx.send(embed=embed)
        except Exception as e:
            logging.critical(f'commands.hof: {e}')
            embed = discord.Embed(colour=constants.COLOUR_ERROR, title=f'Oops, something went wrong')
            await ctx.send(embed=embed)
    
    @commands.Cog.listener()
    async def on_command_error(self, ctx, error):
        username = f'{ctx.message.author.name}#{ctx.message.author.discriminator}'
        logging.error(f'ranking.on_command_error {username}: {error}')