from peewee import *
import datetime
from BaseModel import BaseModel

class RareDefinitionModel(BaseModel):
    pokemon = TextField(primary_key=True)
    rarity = TextField()
    
    class Meta:
        db_table = 'RareDefinition'