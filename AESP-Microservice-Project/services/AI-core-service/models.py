from sqlalchemy import Column, Integer, String, Float, Text, ForeignKey
from database import Base

class Topic(Base):
    __tablename__ = "practice_topics" # Khớp với DB bạn vẽ
    Topic_ID = Column(Integer, primary_key=True, index=True)
    Level_ID = Column(Integer)
    Title = Column(String(255))
    Description = Column(Text)
    Initial_AI_Prompt = Column(Text)

class Session(Base):
    __tablename__ = "ai_sessions" # Khớp với DB bạn vẽ
    Session_ID = Column(Integer, primary_key=True, index=True)
    Learner_ID = Column(Integer) # Tham chiếu logic sang User-service
    Topic_ID = Column(Integer, ForeignKey("practice_topics.Topic_ID"))
    Transcript = Column(Text)
    AI_Grammar_Score = Column(Float)
    AI_Pronunciation_Score = Column(Float)