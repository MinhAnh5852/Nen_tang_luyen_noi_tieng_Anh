
from database import db
from uuid import uuid4
from .enums import AccountStatus,UserRole

class User(db.Model):
    id=db.Column(db.String,primary_key=True,default=lambda:str(uuid4()))
    email=db.Column(db.String,unique=True,nullable=False)
    password=db.Column(db.String,nullable=False)
    role=db.Column(db.Enum(UserRole))
    status=db.Column(db.Enum(AccountStatus),default=AccountStatus.ACTIVE)
