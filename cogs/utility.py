import discord
from peewee import *
from discord.ext import commands, flags
from datetime import datetime
import string
import asyncio
import logging

import utility
import constants
from PokemonModel import PokemonModel

class Utility(commands.Cog):
    def __init__(self, bot, settings):
        self.bot = bot
        self.settings = settings
    
    @commands.command(name="catch", help=f'Displays how many times a pokémon has been caught.\n`Usage: {constants.CURRENT_PREFIX}catch <pokemon name>`')
    async def catch(self, ctx, pokemon: str=None):
        if pokemon is None:
            await ctx.send(f'You need to specify a pokémon')
        pokemon = pokemon.lower()
        try:
            pokemon = PokemonModel.get(PokemonModel.pokemon == pokemon)
            time = 'time' if pokemon.catches <= 1 else 'times'
            await ctx.send(f'**{string.capwords(pokemon.pokemon)}** has been caught {pokemon.catches:,} {time}!')
        except DoesNotExist:
            await ctx.send(f'**{string.capwords(pokemon)}** has yet to be caught!')
        except Exception as e:
            logging.critical(f'commands.catch: {e}')
            await ctx.send('Oops, something went wrong')
    
    @commands.command(name='help', help='Displays this help message')
    async def help(self, ctx):
        author = ctx.message.author
        display_hidden_commands = utility.is_admin(author, self.settings)

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