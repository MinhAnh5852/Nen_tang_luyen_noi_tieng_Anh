from database import db
from uuid import uuid4
from sqlalchemy.sql import func
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String(100), primary_key=True, default=lambda: str(uuid4()))
    username = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(100), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) 
    role = db.Column(db.String(20), default="learner")
    status = db.Column(db.String(20), default="active")
    user_level = db.Column(db.String(50), nullable=True)
    
    # --- CẬP NHẬT ĐỂ ĐỒNG BỘ GIAO DIỆN ---
    package_name = db.Column(db.String(50), default='Gói Miễn Phí')
    package_id = db.Column(db.String(50), default='free-id-001') # ID dùng để React so sánh logic
    
    user_level = db.Column(db.String(50), default='A1 (Beginner)')
    current_streak = db.Column(db.Integer, default=0)
    last_practice_date = db.Column(db.Date, nullable=True)
    overall_accuracy = db.Column(db.Float, default=0.0)
    total_learning_points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    ai_comment = db.Column(db.Text, nullable=False)
    sentiment = db.Column(db.String(20))
    target_name = db.Column(db.String(100), default='System')
    rating = db.Column(db.Integer)
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    author = db.relationship('User', backref=db.backref('user_feedbacks', lazy=True))