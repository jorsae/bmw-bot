from peewee import *
import datetime
from models import BaseModel
from datetime import datetime

class UserModel(BaseModel):
    user_id = AutoField()
    discord_id = TextField(unique=True)
    username = TextField()
    class Meta:
        table_name = 'Users'