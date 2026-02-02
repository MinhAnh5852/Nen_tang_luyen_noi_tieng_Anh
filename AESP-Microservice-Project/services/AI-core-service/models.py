from database import db
from datetime import datetime

class PracticeSession(db.Model):
    __tablename__ = 'practice_sessions'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    topic = db.Column(db.String(100))
    duration_seconds = db.Column(db.Integer, default=0)
    accuracy_score = db.Column(db.Float) # Điểm từ Groq trả về
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

class ChatHistory(db.Model):
    __tablename__ = 'chat_histories'
    id = db.Column(db.Integer, primary_key=True)
    user_id = db.Column(db.Integer, nullable=False)
    role = db.Column(db.String(10), nullable=False) # 'user' hoặc 'ai'
    message = db.Column(db.Text, nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow)