# models/mentor_model.py
from database import db
from datetime import datetime
import json

# 1. Class Mentor (Cũ - Giữ nguyên)
class Mentor(db.Model):
    __tablename__ = 'mentors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(50), unique=True, nullable=False)
    full_name = db.Column(db.String(100), nullable=False)
    bio = db.Column(db.Text, nullable=True)
    skills_json = db.Column(db.Text, nullable=True) # Lưu mảng kỹ năng dưới dạng chuỗi JSON
    status = db.Column(db.String(20), default='PENDING') # PENDING, APPROVED, REJECTED
    rating = db.Column(db.Float, default=5.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    @property
    def skills(self):
        try:
            return json.loads(self.skills_json) if self.skills_json else []
        except:
            return []

    def to_dict(self):
        return {
            'id': self.id,
            'user_id': self.user_id,
            'full_name': self.full_name,
            'bio': self.bio,
            'skills': self.skills,
            'status': self.status,
            'rating': self.rating
        }

# 2. Class Message (MỚI THÊM - Để sửa lỗi ImportError)
class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.String(50), nullable=False)   # ID người gửi
    receiver_id = db.Column(db.String(50), nullable=False) # ID người nhận
    receiver_name = db.Column(db.String(100))              # Tên người nhận
    content = db.Column(db.Text, nullable=False)           # Nội dung
    is_read = db.Column(db.Boolean, default=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            'id': self.id,
            'sender_id': self.sender_id,
            'receiver_id': self.receiver_id,
            'receiver_name': self.receiver_name,
            'content': self.content,
            'is_read': self.is_read,
            'created_at': self.created_at.strftime('%Y-%m-%d %H:%M:%S')
        }