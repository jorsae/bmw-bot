from peewee import *
import datetime
from BaseModel import BaseModel

class UserModel(BaseModel):
    user_id = PrimaryKeyField()
    username = TextField()
    catches = IntegerField(default=0)
    class Meta:
        db_table = 'Users'