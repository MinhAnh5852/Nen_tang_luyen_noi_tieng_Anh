from database import db
from uuid import uuid4
class Payment(db.Model):
    id=db.Column(db.String,primary_key=True,default=lambda:str(uuid4()))
    subscription_id=db.Column(db.String)
    status=db.Column(db.String,default="PENDING")
