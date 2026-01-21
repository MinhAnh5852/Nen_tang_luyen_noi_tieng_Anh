from pydantic import BaseModel
from typing import Optional
from datetime import datetime
from enum import Enum

class TicketStatus(str, Enum):
    OPEN = "open"
    IN_PROGRESS = "in_progress"
    RESOLVED = "resolved"
    CLOSED = "closed"

# Ticket schemas
class TicketCreate(BaseModel):
    title: str
    description: str
    category: Optional[str] = "general"

class TicketUpdate(BaseModel):
    status: Optional[TicketStatus] = None
    category: Optional[str] = None

class TicketResponse(BaseModel):
    id: int
    user_id: int
    title: str
    description: str
    status: str
    category: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Feedback schemas
class FeedbackCreate(BaseModel):
    rating: float
    comment: Optional[str] = None
    session_id: Optional[int] = None
    category: Optional[str] = "general"

class FeedbackResponse(BaseModel):
    id: int
    user_id: int
    rating: float
    comment: Optional[str]
    category: str
    created_at: datetime
    
    class Config:
        from_attributes = True

# Report schemas
class ReportRequest(BaseModel):
    start_date: datetime
    end_date: datetime
    user_id: Optional[int] = None