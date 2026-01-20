import re
import base64
from typing import Optional, Tuple
from datetime import datetime

def validate_email(email: str) -> bool:
    """Validate email format"""
    pattern = r'^[a-zA-Z0-9._%+-]+@[a-zA-Z0-9.-]+\.[a-zA-Z]{2,}$'
    return bool(re.match(pattern, email))

def validate_phone(phone: str) -> bool:
    """Validate phone number format"""
    # Đơn giản: 10-15 chữ số
    pattern = r'^\+?[0-9]{10,15}$'
    return bool(re.match(pattern, phone))

def validate_password(password: str) -> Tuple[bool, Optional[str]]:
    """Validate password strength"""
    if len(password) < 8:
        return False, "Password must be at least 8 characters"
    
    if not re.search(r'[A-Z]', password):
        return False, "Password must contain at least one uppercase letter"
    
    if not re.search(r'[a-z]', password):
        return False, "Password must contain at least one lowercase letter"
    
    if not re.search(r'[0-9]', password):
        return False, "Password must contain at least one number"
    
    if not re.search(r'[!@#$%^&*(),.?":{}|<>]', password):
        return False, "Password must contain at least one special character"
    
    return True, None

def validate_audio_file(audio_base64: str, max_size_mb: int = 10) -> bool:
    """Validate audio file"""
    try:
        # Kiểm tra base64
        if not audio_base64 or len(audio_base64) < 100:
            return False
        
        # Decode để kiểm tra kích thước
        decoded = base64.b64decode(audio_base64)
        
        # Kiểm tra kích thước
        if len(decoded) > max_size_mb * 1024 * 1024:
            return False
        
        # Kiểm tra header của file audio phổ biến
        if len(decoded) < 4:
            return False
        
        # WAV header: "RIFF"
        if decoded[:4] == b'RIFF':
            return True
        
        # MP3 header: starts with 0xFF or ID3
        if decoded[:3] == b'ID3' or (decoded[0] == 0xFF and (decoded[1] & 0xE0) == 0xE0):
            return True
        
        # OGG header: "OggS"
        if decoded[:4] == b'OggS':
            return True
        
        # FLAC header: "fLaC"
        if decoded[:4] == b'fLaC':
            return True
        
        # M4A/AAC: starts with "ftyp"
        if len(decoded) > 8 and decoded[4:8] == b'ftyp':
            return True
        
        return False
    
    except Exception:
        return False

def validate_date_range(start_date: datetime, end_date: datetime) -> bool:
    """Validate date range"""
    if start_date > end_date:
        return False
    
    # Không cho phép range quá lớn (1 năm)
    max_range_days = 365
    if (end_date - start_date).days > max_range_days:
        return False
    
    return True

def sanitize_text(text: str, max_length: int = 5000) -> str:
    """Sanitize text input"""
    if not text:
        return ""
    
    # Giới hạn độ dài
    if len(text) > max_length:
        text = text[:max_length]
    
    # Loại bỏ các ký tự nguy hiểm
    text = re.sub(r'<script.*?>.*?</script>', '', text, flags=re.IGNORECASE | re.DOTALL)
    text = re.sub(r'<.*?>', '', text)  # Loại bỏ HTML tags
    text = re.sub(r'[\x00-\x08\x0B\x0C\x0E-\x1F\x7F]', '', text)  # Loại bỏ control characters
    
    # Escape SQL injection
    text = text.replace("'", "''")
    text = text.replace(";", "")
    
    return text.strip()

def validate_language_code(language_code: str) -> bool:
    """Validate language code format (en-US, vi-VN, etc.)"""
    pattern = r'^[a-z]{2,3}-[A-Z]{2,3}$'
    return bool(re.match(pattern, language_code))

def validate_uuid(uuid_str: str) -> bool:
    """Validate UUID format"""
    pattern = r'^[0-9a-f]{8}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{4}-[0-9a-f]{12}$'
    return bool(re.match(pattern, uuid_str.lower()))