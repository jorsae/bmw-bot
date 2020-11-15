from discord import Colour
import re

RARE_DEFINITION_FOLDER = 'RareDefinition'

# Discord
COLOUR_OK = Colour.green()
COLOUR_NEUTRAL = Colour.orange()
COLOUR_ERROR = Colour.red()

PREFIX = "."
DATABASE_FILE = "../bmw.db"
POKETWO = 'Pokétwo#8236'

GET_USER = re.compile('@!?\d{18}')
GET_POKEMON = re.compile('\d{1} .[\w| |:|-]+!')
GET_ALL_NUMBERS = re.compile('\d+')

POKEMON_FILTER_ADDED_POKEDEX = re.compile('.+this is your')