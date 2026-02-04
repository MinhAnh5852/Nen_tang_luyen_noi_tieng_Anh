from database import db
from datetime import datetime
import json

# 1. Class Mentor - ĐÃ CẬP NHẬT ĐỂ KHỚP DATABASE
class Mentor(db.Model):
    __tablename__ = 'mentors'

    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False) # Tăng độ dài lên 100 cho khớp SQL
    username = db.Column(db.String(100)) # MỚI THÊM: Để không bị lỗi 500
    email = db.Column(db.String(100))    # MỚI THÊM: Để không bị lỗi 500
    full_name = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True) # ĐÃ ĐỔI TÊN: Từ skills_json thành skills
    status = db.Column(db.String(20), default='pending') # ĐỂ CHỮ THƯỜNG: pending
    rating = db.Column(db.Float, default=5.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        # Hàm xử lý skills để trả về mảng cho Frontend (quanlimentor.html)
        skills_list = []
        if self.skills:
            # Nếu lưu dạng "Java, Python" thì split, nếu lưu JSON thì loads
            if '[' in self.skills: 
                try: skills_list = json.loads(self.skills)
                except: skills_list = [s.strip() for s in self.skills.split(',')]
            else:
                skills_list = [s.strip() for s in self.skills.split(',')]

        return {
            'id': self.user_id, # Frontend dùng user_id làm định danh
            'username': self.username or "N/A",
            'email': self.email or "N/A",
            'full_name': self.full_name or self.username,
            'bio': self.bio,
            'skills': skills_list,
            'status': self.status.lower() if self.status else 'pending',
            'rating': self.rating
        }

# 2. Class Message (Giữ nguyên logic của bạn)
class Message(db.Model):
    __tablename__ = 'messages'

    id = db.Column(db.Integer, primary_key=True)
    sender_id = db.Column(db.String(100), nullable=False)   
    receiver_id = db.Column(db.String(100), nullable=False) 
    receiver_name = db.Column(db.String(100))              
    content = db.Column(db.Text, nullable=False)           
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