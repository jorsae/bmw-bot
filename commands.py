from peewee import *
import discord
import string
import logging
import asyncio

import constants
import query
import utility
from UserStatModel import UserStatModel
from UserModel import UserModel
from PokemonModel import PokemonModel

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