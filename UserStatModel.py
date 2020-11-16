from peewee import *
import datetime
from BaseModel import BaseModel
from UserModel import UserModel

class UserStatModel(BaseModel):
    userstat_id = PrimaryKeyField()
    date = DateTimeField(default=datetime.datetime.now().date)
    catches = IntegerField(default=0)
    legendary = IntegerField(default=0)
    mythical = IntegerField(default=0)
    ultrabeast = IntegerField(default=0)
    shiny = IntegerField(default=0)
    user_id = ForeignKeyField(UserModel, to_field='user_id')
    class Meta:
        db_table = 'UserStat'