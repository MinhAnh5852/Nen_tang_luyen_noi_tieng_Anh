from fastapi import APIRouter, Depends, HTTPException, WebSocket, WebSocketDisconnect, status
from sqlalchemy.orm import Session
from typing import List, Optional
import json
import asyncio

from database import get_db
from models.chat_session import ChatSession
from models.chat_message import ChatMessage
from schemas.chat_schemas import (
    SessionCreate, SessionResponse, 
    MessageCreate, MessageResponse,
    AudioUploadRequest, AudioAnalysisResponse
)
from utils.validators import sanitize_text
from services.chat_service import ChatService
from services.websocket_manager import WebSocketManager
from services.ai_processor import AIProcessor
from utils.validators import validate_audio_file

router = APIRouter(prefix="/api/chat", tags=["chat"])
websocket_manager = WebSocketManager()
ai_processor = AIProcessor()

@router.post("/sessions", response_model=SessionResponse)
async def create_chat_session(
    session_data: SessionCreate,
    db: Session = Depends(get_db),
    current_user_id: int = 1  # In real app, get from auth token
):
    """Tạo phiên chat mới"""
    chat_service = ChatService(db)
    session = await chat_service.create_session(
        user_id=current_user_id,
        topic=session_data.topic,
        difficulty_level=session_data.difficulty_level,
        language_focus=session_data.language_focus
    )
    return session

@router.get("/sessions/{session_id}", response_model=SessionResponse)
async def get_chat_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Lấy thông tin phiên chat"""
    chat_service = ChatService(db)
    session = chat_service.get_session(session_id)
    if not session:
        raise HTTPException(status_code=404, detail="Session not found")
    return session

@router.get("/sessions/{session_id}/messages", response_model=List[MessageResponse])
async def get_session_messages(
    session_id: int,
    limit: int = 50,
    offset: int = 0,
    db: Session = Depends(get_db)
):
    """Lấy lịch sử tin nhắn của phiên chat"""
    chat_service = ChatService(db)
    messages = chat_service.get_messages(session_id, limit, offset)
    return messages

@router.post("/sessions/{session_id}/messages", response_model=MessageResponse)
async def send_message(
    session_id: int,
    message_data: MessageCreate,
    db: Session = Depends(get_db)
):
    # Sanitize input trước khi xử lý
    message_data.text = sanitize_text(message_data.text)

    """Gửi tin nhắn text đến AI"""
    chat_service = ChatService(db)
    
    # Lưu tin nhắn của user
    user_message = await chat_service.save_user_message(
        session_id=session_id,
        text=message_data.text,
        message_type="text"
    )
    
    # Gửi đến AI để xử lý
    ai_response = await ai_processor.process_user_message(
        user_message = message_data.text,
        session_id=session_id,
        language_focus=message_data.language_focus
    )
    
    # Lưu phản hồi của AI
    ai_message = await chat_service.save_ai_message(
        session_id=session_id,
        original_text=message_data.text,
        corrected_text=ai_response.get("corrected_text"),
        ai_response=ai_response.get("ai_response"),
        grammar_errors=ai_response.get("grammar_errors"),
        pronunciation_score=ai_response.get("pronunciation_score"),
        vocabulary_complexity=ai_response.get("vocabulary_complexity")
    )
    
    return ai_message

@router.post("/audio/upload", response_model=AudioAnalysisResponse)
async def upload_audio_file(
    audio_data: AudioUploadRequest,
    db: Session = Depends(get_db)
):
    """Upload file audio và nhận phân tích"""
    # Validate audio file
    if not validate_audio_file(audio_data.audio_base64):
        raise HTTPException(status_code=400, detail="Invalid audio file format")
    
    chat_service = ChatService(db)
    
    # Chuyển đổi audio thành text
    text_result = await ai_processor.speech_to_text(
        audio_base64=audio_data.audio_base64,
        language_code=audio_data.language_code or "en-US"
    )
    

    # Phân tích text
    analysis = await ai_processor.analyze_speech(
        text=text_result["text"],
        audio_duration=audio_data.duration
    )
    
    # Lưu kết quả nếu có session_id
    if audio_data.session_id:
        message = await chat_service.save_user_message(
            session_id=audio_data.session_id,
            text=text_result["text"],
            message_type="audio",
            audio_url=audio_data.audio_url,
            audio_duration=audio_data.duration,
            pronunciation_score=analysis.get("pronunciation_score")
        )
        analysis["message_id"] = message.id
    
    return AudioAnalysisResponse(
        text=text_result["text"],
        confidence=text_result["confidence"],
        **analysis
    )

@router.post("/sessions/{session_id}/end", response_model=SessionResponse)
async def end_chat_session(
    session_id: int,
    db: Session = Depends(get_db)
):
    """Kết thúc phiên chat và tính điểm tổng kết"""
    chat_service = ChatService(db)
    session = await chat_service.end_session(session_id)
    return session

# WebSocket endpoint
@router.websocket("/ws/{session_id}")
async def websocket_chat(
    websocket: WebSocket,
    session_id: int,
    token: Optional[str] = None
):
    """WebSocket cho chat real-time với audio streaming"""
    # Xác thực token (trong thực tế)
    # TODO: Xác thực token (trong thực tế)
    # user_id = authenticate_token(token)
    
    await websocket_manager.connect(websocket, session_id)
    
    try:
        while True:
            data = await websocket.receive_json()
            message_type = data.get("type")

            if message_type == "audio_chunk":
                # Xử lý chunk audio
                await handle_audio_chunk(
                    websocket=websocket,
                    session_id=session_id,
                    chunk_data=data.get("data"),
                    timestamp=data.get("timestamp")
                )

            elif message_type == "text_message":
                # Xử lý text message
                await handle_text_message(
                    websocket=websocket,
                    session_id=session_id,
                    text=data.get("text"),
                    message_id=data.get("message_id")
                )

            elif message_type == "typing":
                # User đang typing
                await websocket_manager.broadcast(
                    session_id,
                    {"type": "user_typing", "status": True}
                )
    
    except WebSocketDisconnect:
        websocket_manager.disconnect(websocket, session_id)
    except Exception as e:
        print(f"WebSocket error: {e}")
        await websocket.close()

async def handle_audio_chunk(websocket, session_id, chunk_data, timestamp):
    """Xử lý audio chunk từ client"""
    # Gửi chunk đến AI service để xử lý real-time
    # TODO: Implement audio streaming logic (e.g., send to RabbitMQ or Speech-to-Text stream)
    # TODO: Implement audio streaming logic. 
    # Ví dụ: Đẩy vào RabbitMQ để AI-core-service xử lý hoặc gọi gRPC stream
    pass

async def handle_text_message(websocket, session_id, text, message_id):
    """Xử lý tin nhắn text qua WebSocket"""
    # Gửi đến AI và nhận phản hồi
    ai_response = await ai_processor.process_user_message(
        user_message=text,
        session_id=session_id
    )
    
    # Gửi phản hồi về client
    await websocket.send_json({
        "type": "ai_response",
        "text": ai_response.get("ai_response"),
        "corrections": ai_response.get("corrections"),
        "message_id": message_id
    })