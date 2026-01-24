from sqlalchemy.orm import Session
from sqlalchemy import desc
from typing import List, Optional
from datetime import datetime, timedelta

from models.support_ticket import SupportTicket, TicketStatus
from schemas.support_schemas import TicketCreate, TicketUpdate

class TicketService:
    def __init__(self, db: Session):
        self.db = db
    
    def create_ticket(self, user_id: int, ticket_data: TicketCreate) -> SupportTicket:
        """Tạo ticket mới"""
        ticket = SupportTicket(
            user_id=user_id,
            title=ticket_data.title,
            description=ticket_data.description,
            category=ticket_data.category
        )
        
        self.db.add(ticket)
        self.db.commit()
        self.db.refresh(ticket)
        return ticket
    
    def get_ticket(self, ticket_id: int) -> Optional[SupportTicket]:
        """Lấy ticket theo ID"""
        return self.db.query(SupportTicket).filter(SupportTicket.id == ticket_id).first()
    
    def get_user_tickets(
        self, 
        user_id: int, 
        limit: int = 20, 
        skip: int = 0
    ) -> List[SupportTicket]:
        """Lấy tickets của user"""
        return (self.db.query(SupportTicket)
                .filter(SupportTicket.user_id == user_id)
                .order_by(desc(SupportTicket.created_at))
                .offset(skip)
                .limit(limit)
                .all())
    
    def update_ticket(
        self, 
        ticket_id: int, 
        update_data: TicketUpdate
    ) -> Optional[SupportTicket]:
        """Cập nhật ticket"""
        ticket = self.get_ticket(ticket_id)
        if not ticket:
            return None
        
        for key, value in update_data.dict(exclude_unset=True).items():
            setattr(ticket, key, value)
        
        ticket.updated_at = datetime.utcnow()
        self.db.commit()
        self.db.refresh(ticket)
        return ticket
    
    def get_ticket_stats(self, days: int = 30) -> dict:
        """Lấy thống kê tickets"""
        start_date = datetime.utcnow() - timedelta(days=days)
        
        # Tổng số tickets
        total = self.db.query(SupportTicket).filter(
            SupportTicket.created_at >= start_date
        ).count()
        
        # Theo status
        open_count = self.db.query(SupportTicket).filter(
            SupportTicket.status == TicketStatus.OPEN,
            SupportTicket.created_at >= start_date
        ).count()
        
        resolved_count = self.db.query(SupportTicket).filter(
            SupportTicket.status == TicketStatus.RESOLVED,
            SupportTicket.created_at >= start_date
        ).count()
        
        return {
            "total": total,
            "open": open_count,
            "resolved": resolved_count,
            "resolution_rate": round(resolved_count / total * 100, 2) if total > 0 else 0
        }