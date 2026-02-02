import os
from groq import Groq
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def transcribe_audio(audio_file):
    """
    Nhận vào một file object (từ Flask request) và trả về văn bản.
    """
    try:
        # Groq hỗ trợ model whisper-large-v3 (rất chính xác)
        transcription = client.audio.transcriptions.create(
            file=(audio_file.filename, audio_file.read()), # Gửi dạng tuple (tên file, nội dung bytes)
            model="whisper-large-v3",
            response_format="json",
            language="en", # Chỉ định tiếng Anh để tối ưu (hoặc bỏ đi để auto-detect)
            temperature=0.0
        )
        return transcription.text
    except Exception as e:
        print(f"Error calling Groq STT: {e}")
        return {"error": str(e)}