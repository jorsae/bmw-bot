from peewee import *
from datetime import date
from models import BaseModel, UserModel

class RankRewardModel(BaseModel):
    rank_reward_id = AutoField()
    start_date = DateField(default=date.today())
    reward_type = TextField(default='week')
    place_1 = TextField()
    place_2 = TextField()
    place_3 = TextField()

    class Meta:
        table_name = 'RankReward'