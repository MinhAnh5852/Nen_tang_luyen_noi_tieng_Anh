from fastapi import APIRouter, Depends, HTTPException, UploadFile, File, Form
from sqlalchemy.orm import Session
from typing import Optional
import base64
import tempfile
import os

from database import get_db
from schemas.chat_schemas import AudioAnalysisResponse
from services.speech_service import SpeechService
from services.chat_service import ChatService
from utils.audio_utils import validate_audio_file, convert_audio_format

router = APIRouter(prefix="/api/chat/audio", tags=["audio"])

@router.post("/upload-file", response_model=AudioAnalysisResponse)
async def upload_audio_file(
    file: UploadFile = File(...),
    session_id: Optional[int] = Form(None),
    language_code: str = Form("en-US"),
    db: Session = Depends(get_db)
):
    """Upload file audio và phân tích"""
    # Validate file type
    if not file.filename.endswith(('.wav', '.mp3', '.m4a', '.ogg', '.flac')):
        raise HTTPException(
            status_code=400, 
            detail="Unsupported file format. Supported: wav, mp3, m4a, ogg, flac"
        )
    
    # Lưu file tạm
    with tempfile.NamedTemporaryFile(delete=False, suffix=os.path.splitext(file.filename)[1]) as tmp:
        content = await file.read()
        
        # Kiểm tra kích thước file (max 10MB)
        if len(content) > 10 * 1024 * 1024:
            raise HTTPException(status_code=400, detail="File size exceeds 10MB limit")
        
        tmp.write(content)
        tmp_path = tmp.name
    
    try:
        speech_service = SpeechService()
        chat_service = ChatService(db)
        
        # Phân tích audio
        analysis_result = await speech_service.analyze_audio_file(
            file_path=tmp_path,
            language_code=language_code
        )
        
        # Lưu message nếu có session_id
        if session_id and analysis_result.get("text"):
            message = await chat_service.save_user_message(
                session_id=session_id,
                text=analysis_result["text"],
                message_type="audio",
                audio_url=f"/audio/{os.path.basename(tmp_path)}",
                audio_duration=analysis_result.get("duration"),
                pronunciation_score=analysis_result.get("pronunciation_score")
            )
            analysis_result["message_id"] = message.id
        
        return AudioAnalysisResponse(**analysis_result)
    
    finally:
        # Xóa file tạm
        if os.path.exists(tmp_path):
            os.unlink(tmp_path)

@router.post("/record", response_model=AudioAnalysisResponse)
async def process_recorded_audio(
    audio_base64: str = Form(...),
    session_id: Optional[int] = Form(None),
    duration: float = Form(...),
    language_code: str = Form("en-US"),
    db: Session = Depends(get_db)
):
    """Xử lý audio đã ghi từ client"""
    speech_service = SpeechService()
    chat_service = ChatService(db)
    
    # Validate audio data
    if not validate_audio_file(audio_base64):
        raise HTTPException(status_code=400, detail="Invalid audio data format")
    
    # Phân tích audio
    analysis_result = await speech_service.analyze_audio_base64(
        audio_base64=audio_base64,
        language_code=language_code,
        duration=duration
    )
    
    # Lưu message nếu có session_id
    if session_id and analysis_result.get("text"):
        message = await chat_service.save_user_message(
            session_id=session_id,
            text=analysis_result["text"],
            message_type="audio",
            audio_duration=duration,
            pronunciation_score=analysis_result.get("pronunciation_score")
        )
        analysis_result["message_id"] = message.id
    
    return AudioAnalysisResponse(**analysis_result)

@router.post("/text-to-speech")
async def text_to_speech(
    text: str = Form(..., min_length=1, max_length=1000),
    voice_id: str = Form("rachel"),
    speed: float = Form(1.0, ge=0.5, le=2.0)
):
    """Chuyển text thành speech"""
    speech_service = SpeechService()
    
    try:
        audio_data = await speech_service.text_to_speech(
            text=text,
            voice_id=voice_id,
            speed=speed
        )
        
        return {
            "audio_url": audio_data.get("audio_url"),
            "duration": audio_data.get("duration"),
            "format": audio_data.get("format")
        }
    
    except Exception as e:
        raise HTTPException(status_code=500, detail=f"TTS error: {str(e)}")

@router.get("/voices")
async def get_available_voices():
    """Lấy danh sách giọng đọc có sẵn"""
    speech_service = SpeechService()
    
    voices = await speech_service.get_available_voices()
    
    return {
        "total": len(voices),
        "voices": voices
    }