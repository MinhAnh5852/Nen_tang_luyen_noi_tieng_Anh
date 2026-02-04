from database import db
from datetime import datetime

class SystemStat(db.Model):
    __tablename__ = 'system_stats'
    
    # Key định danh: 'total_users', 'total_revenue', 'active_mentors', 'ai_sessions'
    key = db.Column(db.String(50), primary_key=True) 
    
    # Dùng Float để lưu được số tiền doanh thu lớn (VND) hoặc các chỉ số thập phân
    value = db.Column(db.Float, default=0.0)
    last_updated = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        return {
            "key": self.key,
            "value": self.value,
            "last_updated": self.last_updated.strftime("%Y-%m-%d %H:%M:%S")
        }

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message = db.Column(db.String(255), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "message": self.message,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }

# ==========================================================
# MỚI: Bảng lưu kết quả luyện tập AI (Dành cho Learner Dashboard)
# ==========================================================
class PracticeSession(db.Model):
    __tablename__ = 'practice_sessions'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    user_id = db.Column(db.String(100), nullable=False, index=True)
    topic = db.Column(db.String(100))
    
    # Thời gian luyện tập tính bằng giây (để SUM ra "1h 30m")
    duration_seconds = db.Column(db.Integer, default=0)
    
    # Điểm số AI chấm (0 - 100)
    accuracy_score = db.Column(db.Float, default=0.0)
    grammar_score = db.Column(db.Float, default=0.0)
    vocabulary_score = db.Column(db.Float, default=0.0)
    
    # Nhận xét chi tiết từ AI
    ai_feedback = db.Column(db.Text)
    
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "topic": self.topic,
            "duration": self.duration_seconds,
            "accuracy": self.accuracy_score,
            "grammar": round(self.grammar_score, 1),
            "vocabulary": round(self.vocabulary_score, 1),
            "feedback": self.ai_feedback,
            "date": self.created_at.strftime("%d/%m/%Y %H:%M")
        }