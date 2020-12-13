from peewee import *
import logging
import json

from models import MedalModel

def get_medals(sum_day, sum_all):
    total_medals = []
    medals_day = get_medals_by_time_category("day")
    medals_all = get_medals_by_time_category("all")
    total_medals.extend(compare_medals(medals_day, sum_day))
    total_medals.extend(compare_medals(medals_all, sum_all))
    return total_medals

def compare_medals(medals, sum):
    total_medals = []
    for medal in medals:
        new_medal = compare_medal(medal, sum)
        if new_medal is not None:
            total_medals.append(new_medal)
    return total_medals

def compare_medal(medal, sum):
    if medal.pokemon_category == 'catches':
        if sum.sum_catches >= medal.value_requirement:
            return medal
    elif medal.pokemon_category == 'legendary':
        if sum.sum_legendary >= medal.value_requirement:
            return medal
    elif medal.pokemon_category == 'mythical':
        if sum.sum_mythical >= medal.value_requirement:
            return medal
    elif medal.pokemon_category == 'ultrabeast':
        if sum.sum_ultrabeast >= medal.value_requirement:
            return medal
    elif medal.pokemon_category == 'shiny':
        if sum.sum_shiny >= medal.value_requirement:
            return medal
    else:
        return None

def get_medals_by_time_category(time_category):
    return (MedalModel
            .select()
            .where(MedalModel.time_category == time_category)
            .order_by(MedalModel.pokemon_category, MedalModel.value_requirement)
            )