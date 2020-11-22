from peewee import *
import datetime
from models import BaseModel, UserModel

class RankModel(BaseModel):
    rank_id = PrimaryKeyField()
    start_date = DateField()
    duration = IntegerField()
    reward = TextField()
    placement = IntegerField()
    user_id = ForeignKeyField(UserModel, to_field='user_id')

    class Meta:
        db_table = 'Rank'