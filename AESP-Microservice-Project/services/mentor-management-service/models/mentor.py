from database import db
import uuid

class MentorProfile(db.Model):
    __tablename__ = 'mentor_profiles'
    
    # ID của hồ sơ mentor (UUID)
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    # ID của user bên bảng users (để liên kết)
    user_id = db.Column(db.String(36), unique=True, nullable=False)
    username = db.Column(db.String(100))
    email = db.Column(db.String(100))
    # Thông tin chuyên môn
    skills = db.Column(db.String(255), default="IELTS, Speaking")
    bio = db.Column(db.Text, nullable=True)
    # Trạng thái duyệt: pending (chờ), active (đã duyệt), rejected (từ chối)
    status = db.Column(db.String(20), default='pending')
    rating = db.Column(db.Float, default=5.0)

    def to_dict(self):
        return {
            "id": self.id,
            "user_id": self.user_id,
            "username": self.username,
            "email": self.email,
            "skills": self.skills.split(',') if self.skills else [],
            "status": self.status,
            "rating": self.rating,
            "bio": self.bio
        }