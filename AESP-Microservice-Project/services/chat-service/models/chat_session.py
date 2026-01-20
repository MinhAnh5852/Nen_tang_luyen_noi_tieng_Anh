from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey, Text
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class ChatSession(Base):
    __tablename__ = "chat_sessions"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    session_code = Column(String(50), unique=True, index=True)
    topic = Column(String(255))
    difficulty_level = Column(String(50), default="beginner")
    language_focus = Column(String(100))  # grammar, pronunciation, vocabulary
    ai_model_used = Column(String(100), default="gpt-4")
    
    # Metrics
    total_messages = Column(Integer, default=0)
    total_speaking_time = Column(Float, default=0.0)  # in seconds
    avg_response_time = Column(Float, default=0.0)
    accuracy_score = Column(Float, default=0.0)
    fluency_score = Column(Float, default=0.0)
    vocabulary_score = Column(Float, default=0.0)
    overall_score = Column(Float, default=0.0)
    
    # Status
    status = Column(String(20), default="active")  # active, completed, cancelled
    start_time = Column(DateTime(timezone=True), server_default=func.now())
    end_time = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    messages = relationship("ChatMessage", back_populates="session", cascade="all, delete-orphan")
    
    def __repr__(self):
        return f"<ChatSession {self.session_code}>"