from sqlalchemy import Column, Integer, String, Text, DateTime, Float
from sqlalchemy.sql import func
from database import Base

class UserFeedback(Base):
    __tablename__ = "user_feedbacks"
    
    id = Column(Integer, primary_key=True, index=True)
    user_id = Column(Integer, nullable=False)
    session_id = Column(Integer, nullable=True)
    rating = Column(Float, nullable=False)  # 1-5 stars
    comment = Column(Text, nullable=True)
    category = Column(String(50), default="general")
    
    # Timestamps
    created_at = Column(DateTime(timezone=True), server_default=func.now())
    
    def __repr__(self):
        return f"<UserFeedback {self.id}: {self.rating} stars>"