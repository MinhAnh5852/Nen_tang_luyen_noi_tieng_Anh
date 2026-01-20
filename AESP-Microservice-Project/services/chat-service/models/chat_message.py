from sqlalchemy import Column, Integer, String, DateTime, Float, JSON, ForeignKey, Text, Boolean
from sqlalchemy.orm import relationship
from sqlalchemy.sql import func
from database import Base

class ChatMessage(Base):
    __tablename__ = "chat_messages"
    
    id = Column(Integer, primary_key=True, index=True)
    session_id = Column(Integer, ForeignKey("chat_sessions.id"), nullable=False)
    message_type = Column(String(20), default="text")  # text, audio, system
    sender_type = Column(String(20), default="user")  # user, ai, system
    
    # Content
    original_text = Column(Text, nullable=True)
    corrected_text = Column(Text, nullable=True)
    ai_response = Column(Text, nullable=True)
    audio_url = Column(String(500), nullable=True)
    audio_duration = Column(Float, nullable=True)  # in seconds
    
    # Analysis
    grammar_errors = Column(JSON, nullable=True)  # List of errors
    pronunciation_score = Column(Float, nullable=True)
    vocabulary_complexity = Column(Float, nullable=True)
    sentiment = Column(String(50), nullable=True)  # positive, negative, neutral
    language_detected = Column(String(10), nullable=True)
    
    # Flags
    needs_review = Column(Boolean, default=False)
    is_corrected = Column(Boolean, default=False)
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    processed_at = Column(DateTime(timezone=True), nullable=True)
    
    # Relationships
    session = relationship("ChatSession", back_populates="messages")
    
    def __repr__(self):
        return f"<ChatMessage {self.id} - {self.sender_type}>"