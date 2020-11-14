from peewee import *
import datetime
from BaseModel import BaseModel

class RareModel(BaseModel):
    rare_id = PrimaryKeyField()
    legendary = IntegerField()
    Mythical = IntegerField()
    UltraBeast = IntegerField()
    Shinies = IntegerField()
    
    class Meta:
        db_table = 'Pokemon'