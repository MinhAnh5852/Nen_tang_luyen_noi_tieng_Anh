from fastapi import APIRouter, Depends, Query
from sqlalchemy.orm import Session
from datetime import datetime, timedelta

from database import get_db
from services.report_service import ReportService

router = APIRouter(prefix="/api/reports", tags=["reports"])

@router.get("/user")
def get_user_report(
    user_id: int = Query(...),
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Lấy báo cáo học tập cho user"""
    service = ReportService(db)
    return service.generate_user_report(user_id, days)

@router.get("/summary")
def get_summary_report(
    days: int = Query(30, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Lấy báo cáo tổng quan"""
    from models.support_ticket import SupportTicket
    from models.user_feedback import UserFeedback
    
    end_date = datetime.utcnow()
    start_date = end_date - timedelta(days=days)
    
    # Tổng số tickets
    total_tickets = db.query(SupportTicket).filter(
        SupportTicket.created_at.between(start_date, end_date)
    ).count()
    
    # Tổng số feedbacks
    total_feedbacks = db.query(UserFeedback).filter(
        UserFeedback.created_at.between(start_date, end_date)
    ).count()
    
    # Rating trung bình
    feedbacks = db.query(UserFeedback).filter(
        UserFeedback.created_at.between(start_date, end_date)
    ).all()
    
    avg_rating = sum(f.rating for f in feedbacks) / len(feedbacks) if feedbacks else 0
    
    return {
        "period": f"Last {days} days",
        "tickets": {
            "total": total_tickets,
            "per_day": round(total_tickets / days, 2)
        },
        "feedbacks": {
            "total": total_feedbacks,
            "average_rating": round(avg_rating, 2)
        }
    }