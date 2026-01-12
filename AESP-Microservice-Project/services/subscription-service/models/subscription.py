from database import db
from uuid import uuid4
from datetime import datetime

class Subscription(db.Model):
    __tablename__ = "subscriptions"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid4()))
    user_id = db.Column(db.String, nullable=False, index=True)
    package_id = db.Column(db.String, nullable=False)

    status = db.Column(db.String, nullable=False, default="ACTIVE")  # ACTIVE | CANCELLED | EXPIRED

    start_date = db.Column(db.DateTime, nullable=False)
    end_date = db.Column(db.DateTime, nullable=False)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
