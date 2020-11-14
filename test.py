import re

GET_POKEMON = re.compile('\d{1} .[\w| |:|-]+!')

text = 'Congratulations 249445353273688064> froakie! You caught a level 32 Flabébé! This is your 100th Geodude! You received 3500 Pokécoins.'

pokemon = GET_POKEMON.search(text).group()
pokemon = pokemon[2:len(pokemon) - 1]
pokemon = pokemon.lower()

print(pokemon)