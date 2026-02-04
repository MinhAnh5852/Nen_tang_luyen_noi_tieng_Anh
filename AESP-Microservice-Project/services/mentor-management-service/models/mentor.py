from database import db
from datetime import datetime
import json
import uuid

class MentorProfile(db.Model):
    __tablename__ = 'mentors' # Dùng đúng tên bảng trong init.sql

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(100), unique=True, nullable=False)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    full_name = db.Column(db.String(100), nullable=True)
    bio = db.Column(db.Text, nullable=True)
    skills = db.Column(db.Text, nullable=True) 
    status = db.Column(db.String(20), default='pending') 
    rating = db.Column(db.Float, default=5.0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        # Xử lý skills an toàn để Frontend không bị lỗi map()
        skills_list = []
        if self.skills:
            if '[' in str(self.skills): 
                try: skills_list = json.loads(self.skills)
                except: skills_list = [s.strip() for s in str(self.skills).split(',')]
            else:
                skills_list = [s.strip() for s in str(self.skills).split(',')]

        return {
            'id': self.user_id, # Frontend dùng user_id để định danh khi Duyệt
            'username': self.username or "N/A",
            'email': self.email or "N/A",
            'full_name': self.full_name or self.username,
            'bio': self.bio,
            'skills': skills_list,
            'status': self.status.lower() if self.status else 'pending',
            'rating': self.rating
        }