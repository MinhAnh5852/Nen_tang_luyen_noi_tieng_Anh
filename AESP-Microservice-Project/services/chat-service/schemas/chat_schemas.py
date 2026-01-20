from pydantic import BaseModel, Field, validator
from typing import Optional, List, Dict
from datetime import datetime
from enum import Enum

class DifficultyLevel(str, Enum):
    BEGINNER = "beginner"
    INTERMEDIATE = "intermediate"
    ADVANCED = "advanced"

class LanguageFocus(str, Enum):
    GRAMMAR = "grammar"
    PRONUNCIATION = "pronunciation"
    VOCABULARY = "vocabulary"
    CONVERSATION = "conversation"
    BUSINESS = "business"

class MessageType(str, Enum):
    TEXT = "text"
    AUDIO = "audio"
    SYSTEM = "system"

class SessionStatus(str, Enum):
    ACTIVE = "active"
    COMPLETED = "completed"
    CANCELLED = "cancelled"

# Session schemas
class SessionCreate(BaseModel):
    topic: Optional[str] = Field(None, max_length=255)
    difficulty_level: DifficultyLevel = DifficultyLevel.BEGINNER
    language_focus: LanguageFocus = LanguageFocus.CONVERSATION

class SessionUpdate(BaseModel):
    topic: Optional[str] = None
    difficulty_level: Optional[DifficultyLevel] = None
    status: Optional[SessionStatus] = None

class SessionResponse(BaseModel):
    id: int
    user_id: int
    session_code: str
    topic: Optional[str]
    difficulty_level: str
    language_focus: str
    status: str
    total_messages: int
    total_speaking_time: float
    accuracy_score: Optional[float]
    fluency_score: Optional[float]
    vocabulary_score: Optional[float]
    overall_score: Optional[float]
    start_time: datetime
    end_time: Optional[datetime]
    
    class Config:
        from_attributes = True

# Message schemas
class MessageCreate(BaseModel):
    text: str = Field(..., min_length=1, max_length=1000)
    message_type: MessageType = MessageType.TEXT
    language_focus: Optional[LanguageFocus] = None

class MessageResponse(BaseModel):
    id: int
    session_id: int
    message_type: str
    sender_type: str
    original_text: Optional[str]
    corrected_text: Optional[str]
    ai_response: Optional[str]
    audio_url: Optional[str]
    audio_duration: Optional[float]
    grammar_errors: Optional[List[Dict]]
    pronunciation_score: Optional[float]
    vocabulary_complexity: Optional[float]
    created_at: datetime
    
    class Config:
        from_attributes = True

# Audio schemas
class AudioUploadRequest(BaseModel):
    audio_base64: str = Field(..., description="Base64 encoded audio data")
    session_id: Optional[int] = None
    audio_url: Optional[str] = None
    duration: Optional[float] = None
    language_code: str = "en-US"
    
    @validator('audio_base64')
    def validate_audio_base64(cls, v):
        if not v or len(v) < 100:
            raise ValueError("Invalid audio data")
        return v

class AudioAnalysisResponse(BaseModel):
    text: str
    confidence: float
    pronunciation_score: Optional[float] = None
    fluency_score: Optional[float] = None
    grammar_errors: Optional[List[Dict]] = None
    suggestions: Optional[List[str]] = None
    message_id: Optional[int] = None

# WebSocket schemas
class WebSocketMessage(BaseModel):
    type: str
    data: Optional[Dict] = None
    timestamp: Optional[float] = None

class AudioChunkData(BaseModel):
    chunk: str  # Base64 encoded audio chunk
    sequence: int
    is_last: bool = False

class TextMessageData(BaseModel):
    text: str
    message_id: Optional[str] = None