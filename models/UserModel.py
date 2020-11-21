from peewee import *
import datetime
from models.BaseModel import BaseModel
from datetime import datetime

class UserModel(BaseModel):
    user_id = PrimaryKeyField()
    discord_id = TextField(unique=True)
    username = TextField()
    class Meta:
        db_table = 'Users'