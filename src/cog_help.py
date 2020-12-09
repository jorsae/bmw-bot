import discord
from discord.utils import get
import string
import logging

import constants
import utility
import query

from models import UserModel

# Helper function: Update shiny hunt post with new entries
async def update_shiny_hunt():
    shiny_hunt = query.get_shiny_hunt()
    
    embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
    
    fields = 1
    output = ''
    for sh in shiny_hunt:
        if len(output) > 900:
            embed.add_field(name=f'Shiny hunters {fields}', value=output)
            output = ''
            fields += 1
        output += f'<@{sh.discord_id}>: {string.capwords(sh.shiny_hunt)}\n'
    
    embed.add_field(name=f'Shiny hunters {fields}', value=output)
    return embed

# Helper function: Get user_id from a guild_id to check the user is in that guild
async def fix_new_roles(bot, guild_id, author_id, shiny_hunt, old_shiny_hunt):
    output = ''
    try:
        guild = bot.get_guild(guild_id)
        user = await guild.fetch_member(author_id)

        # Delete or remove role from user, if other people also have the role
        old_role = get(guild.roles, name=old_shiny_hunt)
        if old_role is not None:
            if len(old_role.members) <= 1:
                await old_role.delete()
            else:
                await user.remove_roles(old_role)
        
        # User is in the guild
        role = get(guild.roles, name=shiny_hunt)
        if role is None:
            if shiny_hunt != 'stop':
                role = await guild.create_role(name=shiny_hunt, mentionable=True)
        output += f'Processed {guild.name} successfully\n'
        await user.add_roles(role)

        return output
    except Exception as e:
        logging.critical(f'fix_new_roles: {e}')
        return None

# Helper function to get a persons level, by role
def get_level(author):
    level_role = 0
    try:
        for role in author.roles:
            if role.name.startswith('Lv '):
                level_role = role
                break
        return int(constants.GET_ALL_NUMBERS.search(level_role.name).group())
    except Exception as e:
        logging.info(f'cog_help.get_level. User does not have any levels(most likely): {e} | {author.roles}')
        return 0

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
    top_rank = rank if current_page == 1 else f'{rank - constants.ITEMS_PER_PAGE + 1} - {rank}'
    
    title, author = utility.get_title_author_by_timeflag(time_flag)
    embed = discord.Embed(colour=constants.COLOUR_NEUTRAL, title=f'Top {top_rank} rankings [{str(title)}]')
    embed.set_footer(text=f'Page: {current_page}/{max_page}')
    embed.set_author(name=f'Time remaining: {str(author)}')

    rank -= constants.ITEMS_PER_PAGE -1
    for user_stat in query:
        user = UserModel.get(UserModel.user_id == user_stat.user_id)
        embed.add_field(name=f'{rank}. {user.username}', value=f'{field_attribute}: {user_stat.sum:,}')
        rank += 1
    return embed