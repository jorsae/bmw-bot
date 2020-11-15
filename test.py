import re

GET_POKEMON = re.compile("\d{1} [\w| |:|\-|′|\.]+!")

def p(s):
    print(GET_POKEMON.search(s))


p('congratulations <@!208812982728261632>! you caught a level 24 Pa′u oricorio! Added to your pokédex!')
p('congratulations <@!564876529251909633>! you caught a level 12 Farfetch′d!')
p('congratulations <@!216077596679602176>! you caught a level 39 Mr. Mime!')
p('congratulations <@!216077596679602176>! you caught a level 26 Mime jr.!')
p('congratulations <@!216077596679602176>! you caught a level 26 Mime jr.! This is your 10th mime jr.!')
p('congratulations <@!216077596679602176>! you caught a level 26 Porygon 2! This is your 10th mime jr.!')
p('congratulations <@!216077596679602176>! you caught a level 26 Porygon-Z! This is your 10th mime jr.!')
p('congratulations <@!216077596679602176>! you caught a level 26 Type: Null! This is your 10th mime jr.!')
p('congratulations <@!216077596679602176>! you caught a level 26 Ho-Oh! This is your 10th mime jr.!')
