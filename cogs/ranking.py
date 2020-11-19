import discord
from peewee import *
from discord.ext import commands, flags
from datetime import datetime, date
import asyncio
import logging


import constants
import utility
import query
import medals
from UserStatModel import UserStatModel
from UserModel import UserModel
from PokemonModel import PokemonModel
from enumeration import TimeFlag, HallOfFame

class Ranking(commands.Cog):
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
    
    @flags.add_flag("--catches", action="store_true", default=True)
    @flags.add_flag("--legendary", action="store_true", default=False)
    @flags.add_flag("--mythical", action="store_true", default=False)
    @flags.add_flag("--ultrabeast", action="store_true", default=False)
    @flags.add_flag("--shiny", action="store_true", default=False)
    @flags.add_flag("--week", action="store_true", default=False)
    @flags.add_flag("--day", action="store_true", default=False)
    @flags.add_flag("--month", action="store_true", default=True)
    @flags.add_flag("--all", action="store_true", default=False)
    @flags.add_flag("page", nargs="?", type=str, default=1)
    @flags.command(name="leaderboard", aliases=['l', 'rank'], help=f'Displays the leaderboard for total catches in BMW.\n`Usage: {constants.CURRENT_PREFIX}leaderboard <page> [flags]`\nTime flags: `--all, --month, --week, --day`\nCategory flags: `--catches, --legendary, --mythical, --ultrabeast, --shiny`')
    async def leaderboard(self, ctx, **flags):
        page = abs(utility.str_to_int(flags['page']))
        if page > 100:
            await ctx.send('Please put a more realistic number...')
            return
        
        date, time_flag = utility.parse_time_flags(**flags)
        attribute, field_attribute = utility.parse_attribute_flags(**flags)
        
        try:
            current_page = page

            top_catches = query.get_top_attribute_desc(attribute, 10, current_page, date)

            message = await ctx.send(embed=self.create_leaderboard_embed(top_catches, page, time_flag, field_attribute))
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
                top_catches = query.get_top_attribute_desc(attribute, 10, current_page, date)
                await message.edit(embed=self.create_leaderboard_embed(top_catches, current_page, time_flag, field_attribute))
                await message.remove_reaction(reaction, user)
        except asyncio.TimeoutError:
            pass
        except Exception as e:
            logging.critical(f'commands.leaderboard: {e}')
            embed = discord.Embed(colour=constants.COLOUR_ERROR, title=f'Oops, something went wrong')
            await ctx.send(embed=embed)

    def create_leaderboard_embed(self, query, page, time_flag, field_attribute):
        rank = (page * 10) - 10 + 1
        top_rank = '10' if page == 1 else f'{(page*10)-9}-{page*10}'
        
        title, author = utility.get_title_author_by_timeflag(time_flag)
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL, title=f'Top {top_rank} rankings [{str(title)}]')
        embed.set_author(name=f'Time remaining: {str(author)}')

        for user_stat in query:
            user = UserModel.get(UserModel.user_id == user_stat.user_id)
            embed.add_field(name=f'{rank}. {user.username}', value=f'{field_attribute}: {user_stat.sum:,}')
            rank += 1
        return embed
    
    @commands.command(name='profile', aliases=['p'], help="Displays your profile")
    async def profile(self, ctx, **flags):
        try:
            user = UserModel.get(UserModel.discord_id == ctx.author.id)
            total = query.get_sum(user.user_id).get()
            stats = f'**Catches: **{total.sum_catches:,}\n'
            stats += f'**Legendary: **{total.sum_legendary}\n'
            stats += f'**Mythical: **{total.sum_mythical}\n'
            stats += f'**Ultra Beast: **{total.sum_ultrabeast}\n'
            stats += f'**Shiny: **{total.sum_shiny}'
            rank = (UserStatModel
                    .select()
                    .group_by(UserStatModel.user_id)
                    .having(fn.SUM(UserStatModel.catches) > total.sum_catches)
                    .count()) + 1

            embed = discord.Embed(colour=constants.COLOUR_NEUTRAL, title=f'{str(ctx.author.name)} Profile')
            embed.set_thumbnail(url=ctx.author.avatar_url)
            embed.add_field(name=f'{rank}. {user.username}', value=f'{stats}', inline=False)
            
            sum_day = query.get_max_day(user.user_id).get()
            sum_all = query.get_sum(user.user_id).get()
            total_medals = medals.get_medals(sum_day, sum_all)

            medals_text = ''
            for medal in query.get_hof_titles(user.user_id):
                medals_text += f'{utility.get_hof_emote(medal)} '
            for medal in total_medals:
                medals_text += f'{medal} '
            embed.add_field(name=f'Medals', value=f'{"You have no medals" if medals_text == "" else medals_text}', inline=False)
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

    @commands.command(name='server', aliases=['s'], help='Displays pokémon statistics for BMW')
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
            
            catches = UserStatModel.select(fn.MAX(UserStatModel.catches)).scalar()
            catches_users = "\n".join(query.get_username_by_stat(UserStatModel.catches, catches))

            legendary = UserStatModel.select(fn.MAX(UserStatModel.legendary)).scalar()
            legendary_users = "\n".join(query.get_username_by_stat(UserStatModel.legendary, legendary))

            mythical = UserStatModel.select(fn.MAX(UserStatModel.mythical)).scalar()
            mythical_users = "\n".join(query.get_username_by_stat(UserStatModel.mythical, mythical))

            ultrabeast = UserStatModel.select(fn.MAX(UserStatModel.ultrabeast)).scalar()
            ultrabeast_users = "\n".join(query.get_username_by_stat(UserStatModel.ultrabeast, ultrabeast))

            shiny = UserStatModel.select(fn.MAX(UserStatModel.shiny)).scalar()
            shiny_users = "\n".join(query.get_username_by_stat(UserStatModel.shiny, shiny))

            max_catches = query.get_max_from_userstatmodel(UserStatModel.catches)
            embed.add_field(name=f'{utility.get_hof_emote(HallOfFame.catches)} All pokémon: {catches:,}', value=f'{catches_users}', inline=False)
            
            max_legendary = query.get_max_from_userstatmodel(UserStatModel.legendary)
            embed.add_field(name=f'{utility.get_hof_emote(HallOfFame.legendary)} Legendary: {legendary}', value=f'{legendary_users}', inline=False)
            
            max_mythical = query.get_max_from_userstatmodel(UserStatModel.mythical)
            embed.add_field(name=f'{utility.get_hof_emote(HallOfFame.mythical)} Mythical: {mythical}', value=f'{mythical_users}', inline=False)

            max_ultrabeast = query.get_max_from_userstatmodel(UserStatModel.ultrabeast)
            embed.add_field(name=f'{utility.get_hof_emote(HallOfFame.ultrabeast)} Ultra Beast: {ultrabeast}', value=f'{ultrabeast_users}', inline=False)

            max_shiny = query.get_max_from_userstatmodel(UserStatModel.shiny)
            embed.add_field(name=f'{utility.get_hof_emote(HallOfFame.shiny)} Shiny: {shiny}', value=f'{shiny_users}', inline=False)
            
            await ctx.send(embed=embed)
        except Exception as e:
            logging.critical(f'commands.hof: {e}')
            embed = discord.Embed(colour=constants.COLOUR_ERROR, title=f'Oops, something went wrong')
            await ctx.send(embed=embed)