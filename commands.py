from peewee import *
import discord
import string
import logging

import constants
import utility
from UserModel import UserModel
from PokemonModel import PokemonModel
from RareModel import RareModel

async def leaderboard(ctx, bot):
    try:
        query = UserModel.select(UserModel).order_by(UserModel.catches.desc()).limit(10)
        
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL, title=f'Top {len(query)} catches!')
        rank = 1
        for user in query:
            embed.add_field(name=f'{rank}. {user.username}', value=f'{user.catches} catches!', inline=True)
            rank += 1
        return embed
    except Exception as e:
        logging.critical(f'commands.leaderboard: {e}')
    embed = discord.Embed(colour=constants.COLOUR_ERROR, title=f'Oops, something went wrong')
    return embed

async def profile(ctx, bot):
    try:
        user = UserModel.get(UserModel.user_id == ctx.author.id)
        rank = UserModel.select().where(UserModel.catches > user.catches).count() + 1
        discord_user = await bot.fetch_user(user.user_id)
        
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL, title=f'{str(ctx.author.name)} Profile')
        embed.set_thumbnail(url=ctx.author.avatar_url)
        embed.add_field(name=f'{rank}. {discord_user.name}#{discord_user.discriminator}', value=f'You have {user.catches} catches!', inline=False)
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
    pokemon = pokemon.lower()
    try:
        pokemon = PokemonModel.get(PokemonModel.pokemon == pokemon)
        time = 'time' if pokemon.catches <= 1 else 'times'
        return f'**{string.capwords(pokemon.pokemon)}** has been caught {pokemon.catches} {time}!'
    except DoesNotExist:
        return f'**{string.capwords(pokemon)}** has yet to be caught!'
    except Exception as e:
        logging.critical(f'commands.catch: {e}')
    return 'Oops, something went wrong'

def rares():
    try:
        rares = RareModel.get(RareModel.rare_id == 1)
        total = rares.legendary + rares.mythical + rares.ultrabeast + rares.shiny
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
        embed.add_field(name='Rare pokémon caught', value=f'**Total:** {total}\n**Legendary**: {rares.legendary}\n**Mythical**: {rares.mythical}\n**Ultra beast**: {rares.ultrabeast}\n**Shiny**: {rares.shiny}')
        return embed
    except DoesNotExist:
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
        embed.add_field(name='Rare pokémon caught', value=f'**Total:** 0\n**Legendary**: 0\n**Mythical**: 0\n**Ultra beast**: 0\n**Shiny**: 0')
        return embed
    except Exception as e:
        logging.critical(f'commands.catch: {e}')
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
                embed.add_field(name=f'{constants.PREFIX}{command}', value=command.help, inline=False)
            last_command = str(command)
    return embed