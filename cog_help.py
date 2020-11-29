import discord
import string

import utility
import constants

from models import UserModel

# Helper function to create embed for 'catch'
def catch_embed(pokemon_catches, current_page, max_page, descending):
    embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
    output_value = ''
    
    rank = utility.get_rank_by_page(current_page) - constants.ITEMS_PER_PAGE + 1
    for pokemon_catch in pokemon_catches:
        output_value += f'**{rank}. {string.capwords(pokemon_catch.pokemon)}: **{pokemon_catch.catches}\n'
        rank += 1
    
    order = 'descending' if descending else 'ascdending'
    embed.add_field(name=f'Most caught pokemon [{order}]', value=output_value)
    embed.set_footer(text=f'Page: {current_page}/{max_page}')
    return embed

# Helper function to create embed for 'leaderboard'
def create_leaderboard_embed(query, current_page, max_page, time_flag, field_attribute):
    rank = utility.get_rank_by_page(current_page)
    top_rank = rank if current_page == 1 else f'{rank} - {rank + constants.ITEMS_PER_PAGE}'
    
    title, author = utility.get_title_author_by_timeflag(time_flag)
    embed = discord.Embed(colour=constants.COLOUR_NEUTRAL, title=f'Top {top_rank} rankings [{str(title)}]')
    embed.set_footer(text=f'Page: {current_page}/{max_page}')
    embed.set_author(name=f'Time remaining: {str(author)}')

    for user_stat in query:
        user = UserModel.get(UserModel.user_id == user_stat.user_id)
        embed.add_field(name=f'{rank}. {user.username}', value=f'{field_attribute}: {user_stat.sum:,}')
        rank += 1
    return embed