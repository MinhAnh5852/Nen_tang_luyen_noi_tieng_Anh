from database import db
from uuid import uuid4
from datetime import datetime

class Payment(db.Model):
    __tablename__ = "payments"

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid4()))

    user_id = db.Column(db.String, nullable=False, index=True)
    subscription_id = db.Column(db.String, nullable=True, index=True)

    amount = db.Column(db.Integer, nullable=False)
    currency = db.Column(db.String, nullable=False, default="VND")
    method = db.Column(db.String, nullable=False)

    status = db.Column(db.String, nullable=False, default="PENDING")  # PENDING | SUCCESS | FAILED
    provider_txn_id = db.Column(db.String, nullable=True, unique=False, index=True)

    created_at = db.Column(db.DateTime, nullable=False, default=datetime.utcnow)
    paid_at = db.Column(db.DateTime, nullable=True)
    package_id = db.Column(db.String, nullable=True)