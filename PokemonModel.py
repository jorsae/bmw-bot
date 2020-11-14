from peewee import *
import datetime
from BaseModel import BaseModel

class PokemonModel(BaseModel):
    pokemon_id = PrimaryKeyField()
    pokemon = TextField()
    catches = IntegerField()
    
    class Meta:
        db_table = 'Pokemon'