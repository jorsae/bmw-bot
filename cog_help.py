import discord
import string

import constants

def catch_embed(pokemon_catches, current_page, max_page, descending):
    embed = discord.Embed(colour=constants.COLOUR_NEUTRAL)
    output_value = ''
    
    rank = (current_page * constants.ITEMS_PER_PAGE) - constants.ITEMS_PER_PAGE + 1
    for pokemon_catch in pokemon_catches:
        output_value += f'**{rank}. {string.capwords(pokemon_catch.pokemon)}: **{pokemon_catch.catches}\n'
        rank += 1
    
    order = 'descending' if descending else 'ascdending'
    embed.add_field(name=f'Most caught pokemon [{order}]', value=output_value)
    embed.set_footer(text=f'Page: {current_page}/{max_page}')
    return embed