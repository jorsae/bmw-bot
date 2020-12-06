from peewee import *
import datetime
from models import BaseModel

class RareDefinitionModel(BaseModel):
    pokemon = TextField(primary_key=True)
    rarity = TextField()
    
    class Meta:
        table_name = 'RareDefinition'