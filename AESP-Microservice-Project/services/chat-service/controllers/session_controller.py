from fastapi import APIRouter, Depends, HTTPException, Query
from sqlalchemy.orm import Session
from typing import List, Optional
from datetime import datetime, timedelta

from database import get_db
from schemas.chat_schemas import SessionResponse, SessionUpdate
from services.chat_service import ChatService

router = APIRouter(prefix="/api/chat/sessions", tags=["sessions"])

@router.get("/", response_model=List[SessionResponse])
async def get_user_sessions(
    user_id: int = Query(..., description="User ID"),
    status: Optional[str] = Query(None, regex="^(active|completed|cancelled)$"),
    limit: int = Query(20, ge=1, le=100),
    offset: int = Query(0, ge=0),
    db: Session = Depends(get_db)
):
    """Lấy danh sách phiên chat của user"""
    chat_service = ChatService(db)
    
    sessions = chat_service.get_user_sessions(
        user_id=user_id,
        status=status,
        limit=limit,
        offset=offset
    )
    
    return sessions

@router.get("/recent", response_model=List[SessionResponse])
async def get_recent_sessions(
    user_id: int = Query(..., description="User ID"),
    hours: int = Query(24, ge=1, le=168),
    db: Session = Depends(get_db)
):
    """Lấy phiên chat gần đây"""
    chat_service = ChatService(db)
    
    # Tính thời gian bắt đầu
    start_time = datetime.utcnow() - timedelta(hours=hours)
    
    sessions = chat_service.get_sessions_by_time_range(
        user_id=user_id,
        start_time=start_time
    )
    
    return sessions

@router.get("/stats")
async def get_session_stats(
    user_id: int = Query(..., description="User ID"),
    days: int = Query(7, ge=1, le=365),
    db: Session = Depends(get_db)
):
    """Lấy thống kê phiên chat"""
    chat_service = ChatService(db)
    
    stats = chat_service.get_session_stats(
        user_id=user_id,
        days=days
    )
    
    return {
        "user_id": user_id,
        "period_days": days,
        "stats": stats
    }

@router.put("/{session_id}", response_model=SessionResponse)
async def update_session(
    session_id: int,
    session_update: SessionUpdate,
    db: Session = Depends(get_db)
):
    """Cập nhật thông tin phiên chat"""
    chat_service = ChatService(db)
    
    session = chat_service.update_session(
        session_id=session_id,
        **session_update.dict(exclude_unset=True)
    )
    
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return session

@router.delete("/{session_id}")
async def delete_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Xóa phiên chat (soft delete)"""
    chat_service = ChatService(db)
    
    success = chat_service.delete_session(session_id)
    
    if not success:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return {"message": "Session deleted successfully"}

@router.get("/{session_id}/summary")
async def get_session_summary(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Lấy tổng kết chi tiết của phiên chat"""
    chat_service = ChatService(db)
    
    summary = chat_service.get_session_summary(session_id)
    
    if not summary:
        raise HTTPException(status_code=404, detail="Session not found")
    
    return summary