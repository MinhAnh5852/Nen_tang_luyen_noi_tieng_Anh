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
    # Giữ default="active" cho learner, nhưng sẽ được ghi đè trong __init__ cho mentor
    status = db.Column(db.String(20), default="active")
    
    # --- CẬP NHẬT ĐỂ ĐỒNG BỘ GIAO DIỆN ---
    package_name = db.Column(db.String(50), default='Gói Miễn Phí')
    package_id = db.Column(db.String(50), default='free-id-001') 
    
    user_level = db.Column(db.String(50), default='0') 
    current_streak = db.Column(db.Integer, default=0)
    last_practice_date = db.Column(db.Date, nullable=True)
    overall_accuracy = db.Column(db.Float, default=0.0)
    total_learning_points = db.Column(db.Integer, default=0)
    created_at = db.Column(db.DateTime, server_default=func.now())
    updated_at = db.Column(db.DateTime, server_default=func.now(), onupdate=func.now())

    # 🔥 HÀM QUAN TRỌNG: Tự động phân loại status khi khởi tạo
    def __init__(self, **kwargs):
        super(User, self).__init__(**kwargs)
        # Ép role về chữ thường để so sánh cho chuẩn
        current_role = str(self.role).lower() if self.role else "learner"
        
        if current_role == 'mentor':
            self.status = 'pending'
        else:
            self.status = 'active'

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
    # Thêm vào cuối file user-service/models/user.py

# user-service/models/user.py

class MentorSelection(db.Model):
    __tablename__ = 'mentor_selections'
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    learner_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    mentor_id = db.Column(db.String(100), db.ForeignKey('users.id'), nullable=False)
    status = db.Column(db.String(20), default='active')
    assigned_at = db.Column(db.DateTime, server_default=func.now()) # Bỏ chữ db. đi vì bạn đã import func ở trên rồi
    
    # Thiết lập relationship để dễ dàng truy vấn tên Mentor/Learner
    mentor = db.relationship('User', foreign_keys=[mentor_id])
    learner = db.relationship('User', foreign_keys=[learner_id])