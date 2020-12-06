from discord import Colour
import re

RARE_DEFINITION_FOLDER = './src/RareDefinition'

ITEMS_PER_PAGE = 10

CATCH_BMW_EASTER_EGG = ['<@!777052225099792386>', '<@777052225099792386>', 'bmw']

# Discord
COLOUR_OK = Colour.green()
COLOUR_NEUTRAL = Colour.orange()
COLOUR_ERROR = Colour.red()

CURRENT_PREFIX = '.'
DEFAULT_PREFIX = "."
DATABASE_FILE = "../production.db"
POKETWO = 'Pokétwo#8236'

GET_USER = re.compile('@!?\d{17,18}')
GET_POKEMON = re.compile("\d{1} [\w| |:|\-|′|\.|%]+!")
GET_ALL_NUMBERS = re.compile('\d+')

REMOVE_EMOTES = re.compile('<.+>')