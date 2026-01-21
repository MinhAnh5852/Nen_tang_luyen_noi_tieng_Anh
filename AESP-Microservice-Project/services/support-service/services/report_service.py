from sqlalchemy.orm import Session
from typing import Dict
from datetime import datetime, timedelta
import pandas as pd

class ReportService:
    def __init__(self, db: Session):
        self.db = db
    
    def generate_user_report(
        self, 
        user_id: int, 
        days: int = 30
    ) -> Dict:
        """Tạo báo cáo học tập cho user"""
        from models.support_ticket import SupportTicket
        from models.user_feedback import UserFeedback
        
        end_date = datetime.utcnow()
        start_date = end_date - timedelta(days=days)
        
        # Lấy tickets
        tickets = self.db.query(SupportTicket).filter(
            SupportTicket.user_id == user_id,
            SupportTicket.created_at.between(start_date, end_date)
        ).all()
        
        # Lấy feedbacks
        feedbacks = self.db.query(UserFeedback).filter(
            UserFeedback.user_id == user_id,
            UserFeedback.created_at.between(start_date, end_date)
        ).all()
        
        # Tính toán metrics
        ticket_count = len(tickets)
        avg_rating = sum(f.rating for f in feedbacks) / len(feedbacks) if feedbacks else 0
        
        # Phân tích theo category
        categories = {}
        for ticket in tickets:
            categories[ticket.category] = categories.get(ticket.category, 0) + 1
        
        return {
            "user_id": user_id,
            "period_days": days,
            "tickets": {
                "total": ticket_count,
                "by_category": categories,
                "resolution_rate": self._calculate_resolution_rate(tickets)
            },
            "feedbacks": {
                "total": len(feedbacks),
                "average_rating": round(avg_rating, 2),
                "distribution": self._get_rating_distribution(feedbacks)
            },
            "summary": self._generate_summary(ticket_count, avg_rating)
        }
    
    def _calculate_resolution_rate(self, tickets: list) -> float:
        """Tính tỷ lệ giải quyết"""
        if not tickets:
            return 0.0
        
        resolved = sum(1 for t in tickets if t.status in ["resolved", "closed"])
        return round(resolved / len(tickets) * 100, 2)
    
    def _get_rating_distribution(self, feedbacks: list) -> Dict:
        """Phân phối rating"""
        distribution = {1: 0, 2: 0, 3: 0, 4: 0, 5: 0}
        
        for feedback in feedbacks:
            rating = round(feedback.rating)
            if 1 <= rating <= 5:
                distribution[rating] += 1
        
        return distribution
    
    def _generate_summary(self, ticket_count: int, avg_rating: float) -> str:
        """Tạo summary text"""
        if ticket_count == 0:
            return "No support tickets in this period."
        
        if avg_rating >= 4.5:
            rating_text = "Excellent"
        elif avg_rating >= 4.0:
            rating_text = "Good"
        elif avg_rating >= 3.0:
            rating_text = "Average"
        else:
            rating_text = "Needs improvement"
        
        return f"User submitted {ticket_count} tickets with {rating_text} feedback rating ({avg_rating}/5)."