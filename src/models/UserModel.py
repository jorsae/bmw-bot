from peewee import *
import datetime
from models import BaseModel
from datetime import datetime

class UserModel(BaseModel):
    user_id = AutoField()
    discord_id = TextField(unique=True)
    username = TextField()
    shiny_hunt = TextField(default=None, null=True)
    is_afk = BooleanField(default=False)

    class Meta:
        table_name = 'Users'