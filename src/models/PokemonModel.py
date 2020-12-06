from peewee import *
import datetime
from models import BaseModel

class PokemonModel(BaseModel):
    pokemon = TextField(primary_key=True)
    catches = IntegerField(default=0)
    
    class Meta:
        table_name = 'Pokemon'