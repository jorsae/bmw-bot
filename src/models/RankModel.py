from peewee import *
import datetime
from models import BaseModel, UserModel

class RankModel(BaseModel):
    rank_id = AutoField()
    start_date = DateField()
    duration = IntegerField()
    reward = TextField()
    placement = IntegerField()
    user_id = ForeignKeyField(UserModel, to_field='user_id')

    class Meta:
        table_name = 'Rank'