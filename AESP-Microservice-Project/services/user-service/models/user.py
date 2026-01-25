from database import db
from uuid import uuid4
from sqlalchemy import ForeignKey
from sqlalchemy.orm import relationship

class User(db.Model):
    __tablename__ = 'users'

    id = db.Column(db.String, primary_key=True, default=lambda: str(uuid4()))
    username = db.Column(db.String(100), nullable=True)
    email = db.Column(db.String, unique=True, nullable=False)
    password = db.Column(db.String, nullable=False)
    role = db.Column(db.String(50), default="learner")
    status = db.Column(db.String(50), default="active")
    package_name = db.Column(db.String(50), default='Free')
    user_level = db.Column(db.String(50), default='A1 (Beginner)')
    created_at = db.Column(db.DateTime, server_default=db.func.now())
    updated_at = db.Column(db.DateTime, server_default=db.func.now(), onupdate=db.func.now())

    @property
    def role_str(self):
        return str(self.role).lower() if self.role else ""

# 👇 THÊM CLASS FEEDBACK VÀO ĐÂY 👇
class Feedback(db.Model):
    __tablename__ = 'feedbacks'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    # Lưu ý: user_id phải là String để khớp với id của User (UUID)
    user_id = db.Column(db.String, db.ForeignKey('users.id'), nullable=False)
    target_name = db.Column(db.String(100))
    content = db.Column(db.Text, nullable=False)
    rating = db.Column(db.Integer)
    created_at = db.Column(db.DateTime, server_default=db.func.now())

    # Thiết lập relationship để dễ dàng lấy email từ feedback
    author = db.relationship('User', backref=db.backref('user_feedbacks', lazy=True))