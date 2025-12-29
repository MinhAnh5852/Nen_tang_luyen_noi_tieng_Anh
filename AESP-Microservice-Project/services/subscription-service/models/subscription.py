from database import db
from uuid import uuid4
class Subscription(db.Model):
    id=db.Column(db.String,primary_key=True,default=lambda:str(uuid4()))
    learner_id=db.Column(db.String)
    active=db.Column(db.Boolean,default=True)
