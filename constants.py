import re

PREFIX = "."
DATABASE_FILE = "bmw.db"
POKETWO = 'Pokétwo#8236'

GET_USER = re.compile('@!\d{18}')
GET_POKEMON = re.compile('\d{1} .+!')