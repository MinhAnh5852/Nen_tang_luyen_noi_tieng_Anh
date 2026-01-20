import asyncio
import aiohttp
import base64
import json
import tempfile
import os
from typing import Dict, Optional, List
from openai import AsyncOpenAI
import google.cloud.speech as speech
import google.cloud.texttospeech as tts
from config import settings

class SpeechService:
    def __init__(self):
        self.openai_client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        
        # Initialize Google Cloud clients (if credentials available)
        self.google_speech_client = None
        self.google_tts_client = None
        
        try:
            if os.path.exists(settings.GOOGLE_APPLICATION_CREDENTIALS):
                self.google_speech_client = speech.SpeechClient()
                self.google_tts_client = tts.TextToSpeechClient()
        except Exception as e:
            print(f"Google Cloud initialization failed: {e}")
    
    async def speech_to_text(
        self,
        audio_base64: str,
        language_code: str = "en-US"
    ) -> Dict:
        """Chuyển speech thành text sử dụng Whisper (OpenAI)"""
        
        try:
            # Decode base64 audio
            audio_data = base64.b64decode(audio_base64)
            
            # Lưu tạm file audio
            with tempfile.NamedTemporaryFile(suffix=".wav", delete=False) as tmp:
                tmp.write(audio_data)
                tmp_path = tmp.name
            
            try:
                # Sử dụng Whisper API
                with open(tmp_path, "rb") as audio_file:
                    transcript = await self.openai_client.audio.transcriptions.create(
                        model="whisper-1",
                        file=audio_file,
                        language=language_code.split("-")[0] if language_code else None,
                        response_format="verbose_json"
                    )
                
                result = {
                    "text": transcript.text,
                    "confidence": 0.9,  # Whisper không trả về confidence score
                    "language": transcript.language or language_code,
                    "duration": transcript.duration if hasattr(transcript, 'duration') else None
                }
                
                # Thêm segments nếu có
                if hasattr(transcript, 'segments'):
                    result["segments"] = [
                        {
                            "text": seg.text,
                            "start": seg.start,
                            "end": seg.end,
                            "confidence": getattr(seg, 'confidence', None)
                        }
                        for seg in transcript.segments
                    ]
                
                return result
                
            finally:
                # Xóa file tạm
                if os.path.exists(tmp_path):
                    os.unlink(tmp_path)
                    
        except Exception as e:
            print(f"Speech to text error: {e}")
            
            # Fallback: Google Speech-to-Text
            if self.google_speech_client:
                return await self._google_speech_to_text(audio_base64, language_code)
            
            return {
                "text": "",
                "confidence": 0.0,
                "language": language_code,
                "error": str(e)
            }
    
    async def _google_speech_to_text(
        self,
        audio_base64: str,
        language_code: str = "en-US"
    ) -> Dict:
        """Fallback sử dụng Google Speech-to-Text"""
        try:
            audio_content = base64.b64decode(audio_base64)
            
            audio = speech.RecognitionAudio(content=audio_content)
            config = speech.RecognitionConfig(
                encoding=speech.RecognitionConfig.AudioEncoding.LINEAR16,
                sample_rate_hertz=16000,
                language_code=language_code,
                enable_automatic_punctuation=True,
                model="command_and_search"  # Hoặc "video", "phone_call", etc.
            )
            
            response = self.google_speech_client.recognize(config=config, audio=audio)
            
            if response.results:
                result = response.results[0]
                alternative = result.alternatives[0]
                
                return {
                    "text": alternative.transcript,
                    "confidence": alternative.confidence,
                    "language": language_code
                }
            
            return {
                "text": "",
                "confidence": 0.0,
                "language": language_code
            }
            
        except Exception as e:
            print(f"Google Speech-to-Text error: {e}")
            return {
                "text": "",
                "confidence": 0.0,
                "language": language_code,
                "error": str(e)
            }
    
    async def text_to_speech(
        self,
        text: str,
        voice_id: str = "rachel",
        speed: float = 1.0
    ) -> Dict:
        """Chuyển text thành speech sử dụng ElevenLabs hoặc Google TTS"""
        
        # Thử ElevenLabs trước
        try:
            return await self._elevenlabs_tts(text, voice_id, speed)
        except Exception as e:
            print(f"ElevenLabs TTS failed: {e}")
            
            # Fallback: Google TTS
            if self.google_tts_client:
                return await self._google_tts(text, voice_id, speed)
            
            raise Exception("No TTS service available")
    
    async def _elevenlabs_tts(
        self,
        text: str,
        voice_id: str = "rachel",
        speed: float = 1.0
    ) -> Dict:
        """Sử dụng ElevenLabs API"""
        
        headers = {
            "xi-api-key": settings.ELEVENLABS_API_KEY,
            "Content-Type": "application/json"
        }
        
        data = {
            "text": text,
            "voice_settings": {
                "stability": 0.5,
                "similarity_boost": 0.8,
                "speed": speed
            }
        }
        
        async with aiohttp.ClientSession() as session:
            async with session.post(
                f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
                headers=headers,
                json=data
            ) as response:
                if response.status == 200:
                    audio_data = await response.read()
                    
                    # Lưu file tạm hoặc upload lên storage
                    # Ở đây trả về base64 cho đơn giản
                    audio_base64 = base64.b64encode(audio_data).decode('utf-8')
                    
                    # Ước tính duration (0.05 giây mỗi ký tự)
                    estimated_duration = len(text) * 0.05 * (1 / speed)
                    
                    return {
                        "audio_base64": audio_base64,
                        "duration": estimated_duration,
                        "format": "mp3",
                        "voice_id": voice_id,
                        "provider": "elevenlabs"
                    }
                else:
                    error_text = await response.text()
                    raise Exception(f"ElevenLabs API error: {error_text}")
    
    async def _google_tts(
        self,
        text: str,
        voice_name: str = "en-US-Neural2-F",
        speed: float = 1.0
    ) -> Dict:
        """Sử dụng Google Text-to-Speech"""
        
        synthesis_input = tts.SynthesisInput(text=text)
        
        voice = tts.VoiceSelectionParams(
            language_code="en-US",
            name=voice_name,
            ssml_gender=tts.SsmlVoiceGender.FEMALE
        )
        
        audio_config = tts.AudioConfig(
            audio_encoding=tts.AudioEncoding.MP3,
            speaking_rate=speed,
            pitch=0.0,
            volume_gain_db=0.0
        )
        
        response = self.google_tts_client.synthesize_speech(
            input=synthesis_input,
            voice=voice,
            audio_config=audio_config
        )
        
        audio_base64 = base64.b64encode(response.audio_content).decode('utf-8')
        
        # Ước tính duration
        estimated_duration = len(text) * 0.05 * (1 / speed)
        
        return {
            "audio_base64": audio_base64,
            "duration": estimated_duration,
            "format": "mp3",
            "voice_id": voice_name,
            "provider": "google"
        }
    
    async def analyze_audio_file(
        self,
        file_path: str,
        language_code: str = "en-US"
    ) -> Dict:
        """Phân tích file audio toàn diện"""
        
        # Đọc file
        with open(file_path, "rb") as f:
            audio_data = f.read()
        
        audio_base64 = base64.b64encode(audio_data).decode('utf-8')
        
        # Chuyển thành text
        stt_result = await self.speech_to_text(audio_base64, language_code)
        
        if not stt_result.get("text"):
            return {
                "text": "",
                "confidence": 0.0,
                "error": "No speech detected"
            }
        
        # Phân tích pronunciation (đơn giản)
        pronunciation_score = self._estimate_pronunciation_score(stt_result["text"])
        
        # Tính fluency metrics
        duration = self._get_audio_duration(file_path)
        words_per_minute = self._calculate_words_per_minute(stt_result["text"], duration)
        
        return {
            "text": stt_result["text"],
            "confidence": stt_result.get("confidence", 0.0),
            "pronunciation_score": pronunciation_score,
            "fluency_score": self._calculate_fluency_score(words_per_minute),
            "duration": duration,
            "words_per_minute": words_per_minute,
            "language": stt_result.get("language", language_code)
        }
    
    async def analyze_audio_base64(
        self,
        audio_base64: str,
        language_code: str = "en-US",
        duration: Optional[float] = None
    ) -> Dict:
        """Phân tích audio từ base64"""
        
        # Chuyển thành text
        stt_result = await self.speech_to_text(audio_base64, language_code)
        
        if not stt_result.get("text"):
            return {
                "text": "",
                "confidence": 0.0,
                "error": "No speech detected"
            }
        
        # Tính các metrics
        pronunciation_score = self._estimate_pronunciation_score(stt_result["text"])
        
        if duration:
            words_per_minute = self._calculate_words_per_minute(stt_result["text"], duration)
            fluency_score = self._calculate_fluency_score(words_per_minute)
        else:
            words_per_minute = None
            fluency_score = None
        
        return {
            "text": stt_result["text"],
            "confidence": stt_result.get("confidence", 0.0),
            "pronunciation_score": pronunciation_score,
            "fluency_score": fluency_score,
            "duration": duration,
            "words_per_minute": words_per_minute,
            "language": stt_result.get("language", language_code),
            "segments": stt_result.get("segments", [])
        }
    
    async def get_available_voices(self) -> List[Dict]:
        """Lấy danh sách giọng đọc có sẵn"""
        
        voices = [
            # ElevenLabs voices
            {"id": "rachel", "name": "Rachel", "gender": "female", "accent": "American", "provider": "elevenlabs"},
            {"id": "domi", "name": "Domi", "gender": "female", "accent": "American", "provider": "elevenlabs"},
            {"id": "bella", "name": "Bella", "gender": "female", "accent": "American", "provider": "elevenlabs"},
            {"id": "antoni", "name": "Antoni", "gender": "male", "accent": "American", "provider": "elevenlabs"},
            {"id": "elli", "name": "Elli", "gender": "female", "accent": "American", "provider": "elevenlabs"},
            
            # Google TTS voices
            {"id": "en-US-Neural2-F", "name": "US Female Neural", "gender": "female", "accent": "American", "provider": "google"},
            {"id": "en-US-Neural2-M", "name": "US Male Neural", "gender": "male", "accent": "American", "provider": "google"},
            {"id": "en-GB-Neural2-F", "name": "UK Female Neural", "gender": "female", "accent": "British", "provider": "google"},
            {"id": "en-GB-Neural2-M", "name": "UK Male Neural", "gender": "male", "accent": "British", "provider": "google"},
        ]
        
        return voices
    
    def _estimate_pronunciation_score(self, text: str) -> float:
        """Ước tính điểm phát âm (đơn giản)"""
        # Trong thực tế, cần model phức tạp hơn
        difficult_words = ["thorough", "rural", "sixth", "phenomenon", "anemone"]
        
        words = text.lower().split()
        if not words:
            return 0.0
        
        difficult_count = sum(1 for word in words if word in difficult_words)
        
        # Điểm giảm dần theo số từ khó
        score = 1.0 - (difficult_count / len(words) * 0.3)
        return max(0.0, min(1.0, round(score, 3)))
    
    def _calculate_words_per_minute(self, text: str, duration_seconds: float) -> float:
        """Tính số từ mỗi phút"""
        if duration_seconds <= 0:
            return 0.0
        
        word_count = len(text.split())
        minutes = duration_seconds / 60
        return round(word_count / minutes, 1) if minutes > 0 else 0.0
    
    def _calculate_fluency_score(self, words_per_minute: float) -> float:
        """Tính điểm độ trôi chảy dựa trên WPM"""
        if words_per_minute >= 150:
            return 1.0
        elif words_per_minute >= 120:
            return 0.8
        elif words_per_minute >= 90:
            return 0.6
        elif words_per_minute >= 60:
            return 0.4
        else:
            return 0.2
    
    def _get_audio_duration(self, file_path: str) -> float:
        """Lấy duration của file audio (đơn giản)"""
        try:
            # Sử dụng pydub để lấy duration chính xác
            from pydub import AudioSegment
            
            audio = AudioSegment.from_file(file_path)
            return len(audio) / 1000.0  # Chuyển từ ms sang seconds
        
        except ImportError:
            # Fallback: ước tính dựa trên file size
            file_size = os.path.getsize(file_path)
            # Giả sử 16kHz, 16-bit mono
            bytes_per_second = 16000 * 2
            return file_size / bytes_per_second if bytes_per_second > 0 else 0.0