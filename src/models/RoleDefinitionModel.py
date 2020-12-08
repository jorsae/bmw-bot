from peewee import *
import datetime
from models import BaseModel

class RoleDefinitionModel(BaseModel):
    role = TextField(primary_key=True)
    
    class Meta:
        table_name = 'RoleDefinition'