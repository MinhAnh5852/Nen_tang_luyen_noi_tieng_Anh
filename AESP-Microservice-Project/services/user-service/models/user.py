# from database import db
# from uuid import uuid4
# from sqlalchemy.sql import func

# class User(db.Model):
#     __tablename__ = 'users'

#     # MySQL yêu cầu VARCHAR phải có chiều dài, dùng 36 cho UUID
#     id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
#     username = db.Column(db.String(100), nullable=True)
#     email = db.Column(db.String(150), unique=True, nullable=False)
#     password = db.Column(db.String(255), nullable=False) # Tăng độ dài để chứa Hash password
#     role = db.Column(db.String(50), default="learner")
#     status = db.Column(db.String(50), default="active")
#     package_name = db.Column(db.String(50), default='Free')
#     user_level = db.Column(db.String(50), default='A1 (Beginner)')
#     created_at = db.Column(db.DateTime, server_default=func.now())
#     updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

# class Feedback(db.Model):
#     __tablename__ = 'feedbacks'

#     id = db.Column(db.Integer, primary_key=True, autoincrement=True)
#     # Khớp String(36) với User.id
#     user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
#     target_name = db.Column(db.String(100))
#     content = db.Column(db.Text, nullable=False)
#     rating = db.Column(db.Integer)
#     created_at = db.Column(db.DateTime, server_default=func.now())

#     # Relationship
#     author = db.relationship('User', backref=db.backref('user_feedbacks', lazy=True))
from database import db
from uuid import uuid4
from sqlalchemy.sql import func
from datetime import datetime

class User(db.Model):
    __tablename__ = 'users'

    # MySQL yêu cầu VARCHAR phải có chiều dài, dùng 36 cho UUID
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid4()))
    username = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String(150), unique=True, nullable=False)
    password = db.Column(db.String(255), nullable=False) 
    role = db.Column(db.String(50), default="learner")
    status = db.Column(db.String(50), default="active")
    package_name = db.Column(db.String(50), default='Free')
    user_level = db.Column(db.String(50), default='A1 (Beginner)')
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Khớp String(36) với User.id
    user_id = db.Column(db.String(36), db.ForeignKey('users.id'), nullable=False)
    target_name = db.Column(db.String(100))
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    
    # --- CỘT CÒN THIẾU CỦA BẠN ---
    is_read = db.Column(db.Boolean, default=False) 

    # Relationship để truy xuất thông tin user từ feedback
    author = db.relationship('User', backref=db.backref('user_feedbacks', lazy=True))