from sqlalchemy.orm import Session
from sqlalchemy import and_, desc
from typing import Optional, List
import uuid
from datetime import datetime

from models.chat_session import ChatSession
from models.chat_message import ChatMessage
from schemas.chat_schemas import SessionResponse, MessageResponse

class ChatService:
    def __init__(self, db: Session):
        self.db = db
    
    async def create_session(
        self, 
        user_id: int, 
        topic: Optional[str] = None,
        difficulty_level: str = "beginner",
        language_focus: str = "conversation"
    ) -> ChatSession:
        """Tạo phiên chat mới"""
        session_code = f"CHAT-{uuid.uuid4().hex[:8].upper()}"
        
        session = ChatSession(
            user_id=user_id,
            session_code=session_code,
            topic=topic,
            difficulty_level=difficulty_level,
            language_focus=language_focus,
            status="active"
        )
        
        self.db.add(session)
        self.db.commit()
        self.db.refresh(session)
        
        # Tạo message chào mừng
        welcome_message = ChatMessage(
            session_id=session.id,
            sender_type="ai",
            message_type="system",
            ai_response=f"Hello! I'm your English tutor. Let's practice {topic or 'English conversation'}! I'll help you with your {language_focus}."
        )
        
        self.db.add(welcome_message)
        self.db.commit()
        
        return session
    
    def get_session(self, session_id: int) -> Optional[ChatSession]:
        """Lấy thông tin phiên chat"""
        return self.db.query(ChatSession).filter(ChatSession.id == session_id).first()
    
    def get_user_sessions(
        self, 
        user_id: int, 
        limit: int = 20, 
        offset: int = 0
    ) -> List[ChatSession]:
        """Lấy danh sách phiên chat của user"""
        return (self.db.query(ChatSession)
                .filter(ChatSession.user_id == user_id)
                .order_by(desc(ChatSession.start_time))
                .offset(offset)
                .limit(limit)
                .all())
    
    async def save_user_message(
        self,
        session_id: int,
        text: str,
        message_type: str = "text",
        audio_url: Optional[str] = None,
        audio_duration: Optional[float] = None,
        pronunciation_score: Optional[float] = None
    ) -> ChatMessage:
        """Lưu tin nhắn từ user"""
        message = ChatMessage(
            session_id=session_id,
            sender_type="user",
            message_type=message_type,
            original_text=text,
            audio_url=audio_url,
            audio_duration=audio_duration,
            pronunciation_score=pronunciation_score,
            created_at=datetime.utcnow()
        )
        
        self.db.add(message)
        
        # Update session metrics
        session = self.get_session(session_id)
        if session:
            session.total_messages += 1
            if audio_duration:
                session.total_speaking_time += audio_duration
        
        self.db.commit()
        self.db.refresh(message)
        return message
    
    async def save_ai_message(
        self,
        session_id: int,
        original_text: str,
        corrected_text: Optional[str] = None,
        ai_response: Optional[str] = None,
        grammar_errors: Optional[dict] = None,
        pronunciation_score: Optional[float] = None,
        vocabulary_complexity: Optional[float] = None
    ) -> ChatMessage:
        """Lưu tin nhắn từ AI"""
        message = ChatMessage(
            session_id=session_id,
            sender_type="ai",
            message_type="text",
            original_text=original_text,
            corrected_text=corrected_text,
            ai_response=ai_response,
            grammar_errors=grammar_errors,
            pronunciation_score=pronunciation_score,
            vocabulary_complexity=vocabulary_complexity,
            is_corrected=corrected_text is not None,
            processed_at=datetime.utcnow()
        )
        
        self.db.add(message)
        self.db.commit()
        self.db.refresh(message)
        return message
    
    def get_messages(
        self, 
        session_id: int, 
        limit: int = 50, 
        offset: int = 0
    ) -> List[ChatMessage]:
        """Lấy tin nhắn của phiên chat"""
        return (self.db.query(ChatMessage)
                .filter(ChatMessage.session_id == session_id)
                .order_by(ChatMessage.created_at)
                .offset(offset)
                .limit(limit)
                .all())
    
    async def end_session(self, session_id: int) -> ChatSession:
        """Kết thúc phiên chat và tính điểm"""
        session = self.get_session(session_id)
        if not session:
            raise ValueError("Session not found")
        
        # Tính điểm tổng kết từ tất cả tin nhắn
        messages = self.get_messages(session_id)
        
        if messages:
            # Tính điểm trung bình
            pronunciation_scores = [m.pronunciation_score for m in messages if m.pronunciation_score]
            grammar_scores = [1 if not m.grammar_errors else 0.5 for m in messages if m.sender_type == "user"]
            
            session.pronunciation_score = sum(pronunciation_scores) / len(pronunciation_scores) if pronunciation_scores else 0
            session.grammar_accuracy = sum(grammar_scores) / len(grammar_scores) if grammar_scores else 0
            session.overall_score = (session.pronunciation_score + session.grammar_accuracy) / 2
        
        session.status = "completed"
        session.end_time = datetime.utcnow()
        
        self.db.commit()
        self.db.refresh(session)
        return session