from peewee import *
import datetime
from models import BaseModel, UserModel

class ShinyHuntModel(BaseModel):
    shinyhunt_id = AutoField()
    pokemon = TextField()
    datetime = DateTimeField()
    user_id = ForeignKeyField(UserModel, to_field='user_id')
    
    class Meta:
        table_name = 'ShinyHunt'