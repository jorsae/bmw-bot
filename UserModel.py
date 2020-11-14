from peewee import *
import datetime
from BaseModel import BaseModel

class UserModel(BaseModel):
    user_id = PrimaryKeyField()
    author = TextField()
    catches = IntegerField()
    
    class Meta:
        db_table = 'Users'