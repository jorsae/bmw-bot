from peewee import *
import datetime
from models import BaseModel

class MedalModel(BaseModel):
    medal_id = AutoField()
    description = TextField()
    pokemon_category = TextField()
    value_requirement = IntegerField()
    time_category = TextField()
    medal = TextField()
    class Meta:
        table_name = 'MedalList'