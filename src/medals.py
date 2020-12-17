from peewee import *
import logging
import json

from models import MedalModel

def get_medals(sum_day, sum_all):
    total_medals = []
    total_medals.extend(get_medals_by_time_category("day", sum_day))
    total_medals.extend(get_medals_by_time_category("all", sum_all))
    return total_medals

def get_medals_by_time_category(time_category, sum):
    return (MedalModel
            .select()
            .where(
                (MedalModel.time_category == time_category) &
                    (
                        (
                            (MedalModel.pokemon_category == 'catches') &
                            (sum.sum_catches >= MedalModel.value_requirement)
                        ) |
                        (
                            (MedalModel.pokemon_category == 'legendary') &
                            (sum.sum_legendary >= MedalModel.value_requirement)
                        ) |
                        (
                            (MedalModel.pokemon_category == 'mythical') &
                            (sum.sum_mythical >= MedalModel.value_requirement)
                        ) |
                        (
                            (MedalModel.pokemon_category == 'ultrabeast') &
                            (sum.sum_ultrabeast >= MedalModel.value_requirement)
                        ) |
                        (
                            (MedalModel.pokemon_category == 'shiny') &
                            (sum.sum_shiny >= MedalModel.value_requirement)
                        )
                    )
                )
            .order_by(MedalModel.pokemon_category, MedalModel.value_requirement)
            )