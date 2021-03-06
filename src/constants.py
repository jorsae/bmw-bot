from discord import Colour
import re

# Bot settings
RARE_DEFINITION_FOLDER = './src/RareDefinition'
DEFAULT_PREFIX = "."
DATABASE_FILE = "../production.sql"
POKETWO = 'Pokétwo#8236'

# Bot preferences
ADMIN_LIST = []
MODERATOR_LIST = []
ITEMS_PER_PAGE = 10
MEDALS_PER_ROW = 4
MINIMUM_LEVEL_SHINY_HUNT = 8
ORIGINAL_BMW_SERVER = 565046418990039042
AFK_PREFIX = '[AFK] '
CATCH_BMW_EASTER_EGG = ['<@!777052225099792386>', '<@777052225099792386>', 'bmw']
BMW_SERVERS = [565046418990039042, 738333789985439804, 739812982128902265, 740388361247916062, 745918772266663956, 742718014717296751, 742916841063710801, 744204921686982667]
LOADED_BMW_SERVERS = []

# Discord settings
COLOUR_OK = Colour.green()
COLOUR_NEUTRAL = Colour.orange()
COLOUR_ERROR = Colour.red()
MAX_NICKNAME_LENGTH = 32

GET_USER = re.compile('@!?\d{17,18}')
GET_POKEMON = re.compile("\d{1} [\w| |:|\-|′|\.|%]+!")
GET_ALL_NUMBERS = re.compile('\d+')