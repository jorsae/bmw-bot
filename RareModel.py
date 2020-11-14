from peewee import *
import datetime
from BaseModel import BaseModel

class RareModel(BaseModel):
    rare_id = PrimaryKeyField()
    legendary = IntegerField(default=0)
    mythical = IntegerField(default=0)
    ultrabeast = IntegerField(default=0)
    shiny = IntegerField(default=0)
    
    class Meta:
        db_table = 'RareCount'