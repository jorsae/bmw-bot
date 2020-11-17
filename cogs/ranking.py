import discord
from peewee import *
from discord.ext import commands, flags
from datetime import datetime
import asyncio
import logging


import constants
import utility
import query
from titles import HallOfFame
from UserStatModel import UserStatModel
from UserModel import UserModel
from PokemonModel import PokemonModel

class Ranking(commands.Cog):
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
    
    @flags.add_flag("--all", action="store_true", default=False)
    @flags.add_flag("page", nargs="?", type=str, default=1)
    @flags.command(name="leaderboard", help=f'Displays the leaderboard for total catches in BMW.\nUsage: {constants.CURRENT_PREFIX}leaderboard <page> --all')
    async def leaderboard(self, ctx, **flags):
        page = abs(utility.str_to_int(flags['page']))
        
        date = utility.get_date_current_month()
        if flags["all"]:
            date = utility.get_date_forever_ago()
        
        try:
            current_page = page

            top_catches = query.get_top_catches_desc(10, current_page, date)

            message = await ctx.send(embed=self.create_leaderboard_embed(top_catches, page))
            await message.add_reaction("◀️")
            await message.add_reaction("▶️")
            
            def check(reaction, user):
                if reaction.message.id == message.id:
                    return user == ctx.author and str(reaction.emoji) in ["◀️", "▶️"]
                else:
                    return False
            
            while True:
                reaction, user = await self.bot.wait_for("reaction_add", timeout=60, check=check)
                if str(reaction.emoji) == "▶️":
                    current_page += 1
                elif str(reaction.emoji) == "◀️" and current_page > 1:
                    current_page -= 1
                top_catches = query.get_top_catches_desc(10, current_page, date)
                await message.edit(embed=self.create_leaderboard_embed(top_catches, current_page))
                await message.remove_reaction(reaction, user)
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            logging.critical(f'commands.leaderboard: {e}')
            embed = discord.Embed(colour=constants.COLOUR_ERROR, title=f'Oops, something went wrong')
            await ctx.send(embed=embed)

    def create_leaderboard_embed(self, query, page):
        rank = (page * 10) - 10 + 1
        top_rank = '10' if page == 1 else f'{(page*10)-9}-{page*10}'
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL, title=f'Top {top_rank} rankings')
        for user_stat in query:
            user = UserModel.get(UserModel.user_id == user_stat.user_id)
            embed.add_field(name=f'{rank}. {user.username}', value=f'{user_stat.sum:,} catches!')
            rank += 1
        return embed
    
    @commands.command(name="profile", help="Displays your profile")
    async def profile(self, ctx):
        try:
            user = UserModel.get(UserModel.discord_id == ctx.author.id)
            catches = (UserStatModel
                        .select(fn.SUM(UserStatModel.catches).alias("sum"))
                        .where(UserStatModel.user_id == user.user_id)
                        .scalar())
            
            rank = (UserStatModel
                    .select()
                    .group_by(UserStatModel.user_id)
                    .having(fn.SUM(UserStatModel.catches) > catches)
                    .count()) + 1
            
            titles = query.get_hof_titles(user.user_id)

            embed = discord.Embed(colour=constants.COLOUR_NEUTRAL, title=f'{str(ctx.author.name)} Profile')
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.add_field(name=f'{rank}. {user.username}', value=f'You have {catches:,} catches!')
            medals = ''
            for title in titles:
                medals += f'{utility.get_hof_emote(title)} '
            embed.add_field(name=f'Medals', value=f'{"You have no medals" if medals == "" else medals}')
            await ctx.send(embed=embed)
        except DoesNotExist:
            embed = discord.Embed(colour=constants.COLOUR_NEUTRAL, title=f'{str(ctx.author.name)} Profile')
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.add_field(name=f'You have not caught any pokémon', value=f'Go catch pokémon!')
            await ctx.send(embed=embed)
        except Exception as e:
            logging.critical(f'commands.profile: {e}')
            embed = discord.Embed(colour=constants.COLOUR_ERROR, title=f'Oops, something went wrong')
            await ctx.send(embed=embed)

    @commands.command(name="server", help='Displays pokémon statistics for BMW')
    async def server(self, ctx):
        total_caught = await query.get_pokemon_caught()
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

    @commands.command(name="rares", help=f'Displays how many rare pokémon have been caught')
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
            embed = discord.Embed(colour=constants.COLOUR_NEUTRAL, title='Hall of Fame')
            
            catches = UserStatModel.select(fn.MAX(UserStatModel.catches)).scalar()
            legendary = UserStatModel.select(fn.MAX(UserStatModel.legendary)).scalar()
            mythical = UserStatModel.select(fn.MAX(UserStatModel.mythical)).scalar()
            ultrabeast = UserStatModel.select(fn.MAX(UserStatModel.ultrabeast)).scalar()
            shiny = UserStatModel.select(fn.MAX(UserStatModel.shiny)).scalar()

            max_catches = query.get_max_from_userstatmodel(UserStatModel.catches)
            name = utility.get_text_from_hof(max_catches)
            embed.add_field(name=f'{utility.get_hof_emote(HallOfFame.catches)} Most catches: {catches}', value=f'{name}')
            
            max_legendary = query.get_max_from_userstatmodel(UserStatModel.legendary)
            name = utility.get_text_from_hof(max_legendary)
            embed.add_field(name=f'{utility.get_hof_emote(HallOfFame.legendary)} Legendary: {legendary}', value=f'{name}')
            
            max_mythical = query.get_max_from_userstatmodel(UserStatModel.mythical)
            name = utility.get_text_from_hof(max_mythical)
            embed.add_field(name=f'{utility.get_hof_emote(HallOfFame.mythical)} Mythical: {mythical}', value=f'{name}')

            max_ultrabeast = query.get_max_from_userstatmodel(UserStatModel.ultrabeast)
            name = utility.get_text_from_hof(max_ultrabeast)
            embed.add_field(name=f'{utility.get_hof_emote(HallOfFame.ultrabeast)} Ultra Beast: {ultrabeast}', value=f'{name}')

            max_shiny = query.get_max_from_userstatmodel(UserStatModel.shiny)
            name = utility.get_text_from_hof(max_shiny)
            embed.add_field(name=f'{utility.get_hof_emote(HallOfFame.shiny)} Shiny: {shiny}', value=f'{name}')
            
            await ctx.send(embed=embed)
        except Exception as e:
            logging.critical(f'commands.hof: {e}')
            embed = discord.Embed(colour=constants.COLOUR_ERROR, title=f'Oops, something went wrong')
            await ctx.send(embed=embed)