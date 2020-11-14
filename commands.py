from peewee import *
import discord
import logging

import constants
from UserModel import UserModel

async def leaderboard(ctx, bot):
    try:
        query = UserModel.select(UserModel).order_by(UserModel.catches.desc()).limit(10)
        
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL, title=f'Top 10 catches!')
        rank = 1
        for user in query:
            discord_user = await bot.fetch_user(user.user_id)
            embed.add_field(name=f'{rank}. {discord_user.name}#{discord_user.discriminator}', value=f'{user.catches} catches!', inline=False)
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
        embed.add_field(name=f'{rank}. {discord_user.name}#{discord_user.discriminator}', value=f'You have {user.catches} catches!', inline=False)
        return embed
    except DoesNotExist:
        embed = discord.Embed(colour=constants.COLOUR_NEUTRAL, title=f'{str(ctx.author.name)} Profile')
        embed.add_field(name=f'You have not caught any pokemon', value=f'Go catch pokémon!')
        return embed
    except Exception as e:
        logging.critical(f'commands.leaderboard: {e}')
    embed = discord.Embed(colour=constants.COLOUR_ERROR, title=f'Oops, something went wrong')
    return embed