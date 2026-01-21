from fastapi import APIRouter, Depends, HTTPException
from sqlalchemy.orm import Session
from typing import List

from database import get_db
from schemas.support_schemas import (
    TicketCreate, TicketUpdate, TicketResponse,
    FeedbackCreate, FeedbackResponse
)
from services.ticket_service import TicketService
from models.user_feedback import UserFeedback

router = APIRouter(prefix="/api/support", tags=["support"])

@router.post("/tickets", response_model=TicketResponse)
def create_ticket(
    ticket_data: TicketCreate,
    db: Session = Depends(get_db),
    user_id: int = 1  # In real app, get from auth
):
    """Tạo ticket hỗ trợ mới"""
    service = TicketService(db)
    return service.create_ticket(user_id, ticket_data)

@router.get("/tickets", response_model=List[TicketResponse])
def get_tickets(
    user_id: int,
    limit: int = 20,
    skip: int = 0,
    db: Session = Depends(get_db)
):
    """Lấy danh sách tickets của user"""
    service = TicketService(db)
    return service.get_user_tickets(user_id, limit, skip)

@router.get("/tickets/{ticket_id}", response_model=TicketResponse)
def get_ticket(
    ticket_id: int,
    db: Session = Depends(get_db)
):
    """Lấy thông tin ticket"""
    service = TicketService(db)
    ticket = service.get_ticket(ticket_id)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return ticket

@router.put("/tickets/{ticket_id}", response_model=TicketResponse)
def update_ticket(
    ticket_id: int,
    update_data: TicketUpdate,
    db: Session = Depends(get_db)
):
    """Cập nhật ticket"""
    service = TicketService(db)
    ticket = service.update_ticket(ticket_id, update_data)
    
    if not ticket:
        raise HTTPException(status_code=404, detail="Ticket not found")
    
    return ticket

@router.post("/feedback", response_model=FeedbackResponse)
def submit_feedback(
    feedback_data: FeedbackCreate,
    db: Session = Depends(get_db),
    user_id: int = 1
):
    """Gửi phản hồi"""
    feedback = UserFeedback(
        user_id=user_id,
        rating=feedback_data.rating,
        comment=feedback_data.comment,
        session_id=feedback_data.session_id,
        category=feedback_data.category
    )
    
    db.add(feedback)
    db.commit()
    db.refresh(feedback)
    
    return feedback

@router.get("/stats")
def get_stats(
    days: int = 30,
    db: Session = Depends(get_db)
):
    """Lấy thống kê tickets"""
    service = TicketService(db)
    return service.get_ticket_stats(days)