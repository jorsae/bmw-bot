from peewee import *
import discord
import string
import logging

import constants
import query
import utility
from UserStatModel import UserStatModel
from UserModel import UserModel
from PokemonModel import PokemonModel
from RareModel import RareModel

async def leaderboard(ctx, bot):
    try:
        query = (UserStatModel
                .select(fn.SUM(UserStatModel.catches).alias("sum"), UserStatModel.user_id)
                .group_by(UserStatModel.user_id)
                .order_by(fn.SUM(UserStatModel.catches).desc())
                .limit(10))

        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL, title=f'Top {len(query)} rankings')
        rank = 1
        for user_stat in query:
            user = UserModel.get(UserModel.user_id == user_stat.user_id)
            embed.add_field(name=f'{rank}. {user.username}', value=f'{user_stat.sum:,} catches!')
            rank += 1
        return embed
    except Exception as e:
        logging.critical(f'commands.leaderboard: {e}')
    embed = discord.Embed(colour=constants.COLOUR_ERROR, title=f'Oops, something went wrong')
    return embed

async def profile(ctx, bot):
    try:
        user = UserModel.get(UserModel.discord_id == ctx.author.id)
        catches = UserStatModel.select(fn.SUM(UserStatModel.catches).alias("sum")).where(UserStatModel.user_id == user.user_id).scalar()
        rank = UserStatModel.select().group_by(UserStatModel.user_id).having(fn.SUM(UserStatModel.catches) > catches).count() + 1
        
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL, title=f'{str(ctx.author.name)} Profile')
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.add_field(name=f'{rank}. {user.username}', value=f'You have {catches:,} catches!', inline=False)
        return embed
    except DoesNotExist:
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL, title=f'{str(ctx.author.name)} Profile')
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.add_field(name=f'You have not caught any pokémon', value=f'Go catch pokémon!')
        return embed
    except Exception as e:
        logging.critical(f'commands.profile: {e}')
    embed = discord.Embed(colour=constants.COLOUR_ERROR, title=f'Oops, something went wrong')
    return embed

def catch(pokemon):
    if pokemon is None:
        return f'You need to specify a pokémon'
    pokemon = pokemon.lower()
    try:
        pokemon = PokemonModel.get(PokemonModel.pokemon == pokemon)
        time = 'time' if pokemon.catches <= 1 else 'times'
        return f'**{string.capwords(pokemon.pokemon)}** has been caught {pokemon.catches:,} {time}!'
    except DoesNotExist:
        return f'**{string.capwords(pokemon)}** has yet to be caught!'
    except Exception as e:
        logging.critical(f'commands.catch: {e}')
    return 'Oops, something went wrong'

def rares():
    try:
        legendary = UserStatModel.select(fn.SUM(UserStatModel.legendary)).scalar()
        mythical = UserStatModel.select(fn.SUM(UserStatModel.mythical)).scalar()
        ultrabeast = UserStatModel.select(fn.SUM(UserStatModel.ultrabeast)).scalar()
        shiny = UserStatModel.select(fn.SUM(UserStatModel.shiny)).scalar()

        total_rares = legendary + mythical + ultrabeast
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
        embed.add_field(name='Rare pokémon caught', value=f'**Total: **{total_rares:,}\n**Legendary: **{legendary:,}\n**Mythical: **{mythical:,}\n**Ultra beast: **{ultrabeast:,}\n**Shiny: **{shiny:,}')
        return embed
    except DoesNotExist:
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
        embed.add_field(name='Rare pokémon caught', value=f'**Total:** 0\n**Legendary**: 0\n**Mythical**: 0\n**Ultra beast**: 0\n**Shiny**: 0')
        return embed
    except Exception as e:
        logging.critical(f'commands.catch: {e}')
    embed = discord.Embed(colour=constants.COLOUR_ERROR, title=f'Oops, something went wrong')
    return embed

async def server():
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
        embed.add_field(name='BMW pokémon stats', value=f'**Total pokémon caught: **{total_caught:,}\n**Total rare pokémon: **{total_rares:,}\n**Percentage rare pokémon: **{percent_rare}%\n**Total shiny pokémon: **{shiny:,}\n**Percentage shiny pokémon: **{percent_shiny}')
        return embed
    except DoesNotExist:
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
        embed.add_field(name='BMW pokémon stats', value=f'**Total pokémon caught:** {total_caught:,}\n**Total rare pokémon:** 0\n**Percentage rare pokémon:** 0%\n**Total shiny pokémon: **0\n**Percentage shiny pokémon **0%')
        return embed
    except Exception as e:
        logging.critical(f'server: {e}')
    embed = discord.Embed(colour=constants.COLOUR_ERROR, title=f'Oops, something went wrong')
    return embed

def help(ctx, settings, bot):
    author = ctx.message.author
    display_hidden_commands = utility.is_admin(author, settings)

    embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
    embed.set_author(name=f'BMW Help')
    last_command = None
    for command in bot.walk_commands():
        command = bot.get_command(str(command))
        if command is None:
            continue
        if command.hidden is False or display_hidden_commands:
            if last_command != str(command):
                embed.add_field(name=f'{settings.prefix}{command}', value=command.help, inline=False)
            last_command = str(command)
    return embed