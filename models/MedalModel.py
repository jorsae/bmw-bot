from peewee import *
import datetime
from models.BaseModel import BaseModel

class MedalModel(BaseModel):
    medal_id = PrimaryKeyField()
    description = TextField()
    pokemon_category = TextField()
    value_requirement = IntegerField()
    time_category = TextField()
    medal = TextField()
    class Meta:
        db_table = 'MedalList'