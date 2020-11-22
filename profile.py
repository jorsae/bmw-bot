import discord
from peewee import *
import logging

import constants
import utility
import query
import medals
from models import *

def get_profile_page(ctx, page, **flags):
    if page <= 1:
        return profile_page_1(ctx, **flags)
    else:
        return profile_page_2(ctx, **flags)

def profile_page_2(ctx, **flags):
    embed = discord.Embed(colour=constants.COLOUR_NEUTRAL, title=f'{str(ctx.author.name)} Profile')
    return embed

def profile_page_1(ctx, **flags):
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
        total = 0
        for medal in query.get_hof_medals(f'{ctx.author.name}#{ctx.author.discriminator}'):
            medals_text += f'{utility.get_hof_emote(medal)} '
            total += 1
        
        if total > 0:
            medals_text += '\n\n'
            total = 0
        
        for medal in total_medals:
            medals_text += f'{medal} '
            total += 1
            if (total % 5) == 0:
                medals_text += '\n'
        embed.add_field(name=f'Medals', value=f'{"You have no medals" if medals_text == "" else medals_text}', inline=False)
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