from openai import AsyncOpenAI
import json
from typing import Dict, Optional, List
from datetime import datetime
from config import settings

class AIProcessor:
    def __init__(self):
        self.client = AsyncOpenAI(api_key=settings.OPENAI_API_KEY)
        self.model = "gpt-4"
        
    async def process_user_message(
        self,
        user_message: str,
        session_id: int,
        language_focus: str = "grammar"
    ) -> Dict:
        """Xử lý tin nhắn từ user và trả về phản hồi của AI"""
        
        prompt = self._build_prompt(user_message, language_focus)
        
        try:
            response = await self.client.chat.completions.create(
                model=self.model,
                messages=[
                    {"role": "system", "content": "You are a friendly English tutor. Your task is to help students improve their English."},
                    {"role": "user", "content": prompt}
                ],
                temperature=0.7,
                max_tokens=500
            )
            
            ai_response = response.choices[0].message.content
            
            # Parse response để lấy corrections
            corrections = self._extract_corrections(ai_response)
            
            return {
                "ai_response": ai_response,
                "corrected_text": corrections.get("corrected_sentence"),
                "grammar_errors": corrections.get("errors", []),
                "pronunciation_score": self._calculate_pronunciation_score(user_message),
                "vocabulary_complexity": self._calculate_vocabulary_complexity(user_message)
            }
            
        except Exception as e:
            print(f"AI Processing error: {e}")
            return {
                "ai_response": "I apologize, but I'm having trouble processing your message. Please try again.",
                "corrected_text": None,
                "grammar_errors": [],
                "pronunciation_score": None,
                "vocabulary_complexity": None
            }
    
    def _build_prompt(self, user_message: str, language_focus: str) -> str:
        """Xây dựng prompt cho AI"""
        
        prompts = {
            "grammar": f"""
            Analyze this English sentence and provide:
            1. Corrected version if there are errors
            2. List of grammar mistakes with explanations
            3. A natural response to continue the conversation
            
            Sentence: "{user_message}"
            
            Format your response as JSON:
            {{
                "corrected_sentence": "corrected version here",
                "errors": [
                    {{
                        "type": "grammar/vocabulary/word_order",
                        "original": "incorrect part",
                        "corrected": "correct version",
                        "explanation": "brief explanation"
                    }}
                ],
                "response": "your natural conversation response"
            }}
            """,
            
            "pronunciation": f"""
            Analyze this sentence for pronunciation issues:
            1. Identify difficult words for non-native speakers
            2. Suggest pronunciation tips
            3. Provide a natural response
            
            Sentence: "{user_message}"
            
            Format response as JSON with pronunciation_feedback and response.
            """,
            
            "conversation": f"""
            Respond naturally to continue the conversation. 
            If there are obvious errors, gently correct them.
            
            User: "{user_message}"
            """
        }
        
        return prompts.get(language_focus, prompts["conversation"])
    
    def _extract_corrections(self, ai_response: str) -> Dict:
        """Trích xuất thông tin sửa lỗi từ phản hồi AI"""
        try:
            # Tìm JSON trong response
            start = ai_response.find('{')
            end = ai_response.rfind('}') + 1
            
            if start != -1 and end != 0:
                json_str = ai_response[start:end]
                return json.loads(json_str)
        except:
            pass
        
        return {"response": ai_response}
    
    def _calculate_pronunciation_score(self, text: str) -> float:
        """Tính điểm phát âm (đơn giản)"""
        # Trong thực tế, cần model phức tạp hơn
        difficult_words = ["thorough", "rural", "sixth", "phenomenon", "anemone"]
        
        words = text.lower().split()
        difficult_count = sum(1 for word in words if word in difficult_words)
        
        if len(words) == 0:
            return 1.0
        
        score = 1.0 - (difficult_count / len(words) * 0.3)
        return round(score, 2)
    
    def _calculate_vocabulary_complexity(self, text: str) -> float:
        """Tính độ phức tạp từ vựng"""
        # Đơn giản: đếm từ dài
        words = text.split()
        if not words:
            return 0.0
        
        long_words = sum(1 for word in words if len(word) > 6)
        complexity = long_words / len(words)
        return round(complexity, 2)
    
    async def speech_to_text(
        self, 
        audio_base64: str, 
        language_code: str = "en-US"
    ) -> Dict:
        """Chuyển đổi speech to text"""
        # Trong thực tế, tích hợp với Google Speech-to-Text, Whisper, etc.
        # Đây là mock implementation
        return {
            "text": "This is a mock transcription of the audio.",
            "confidence": 0.85,
            "language": language_code
        }
    
    async def text_to_speech(
        self, 
        text: str, 
        voice_id: str = "rachel"
    ) -> Dict:
        """Chuyển đổi text to speech"""
        # Trong thực tế, tích hợp với ElevenLabs, Google TTS, etc.
        return {
            "audio_url": f"https://api.elevenlabs.io/v1/text-to-speech/{voice_id}",
            "duration": len(text) * 0.05,  # ước tính
            "format": "mp3"
        }
    
    async def analyze_speech(
        self, 
        text: str, 
        audio_duration: Optional[float] = None
    ) -> Dict:
        """Phân tích bài nói"""
        words_per_minute = len(text.split()) / (audio_duration / 60) if audio_duration else 120
        
        return {
            "words_per_minute": round(words_per_minute, 2),
            "pronunciation_score": self._calculate_pronunciation_score(text),
            "vocabulary_complexity": self._calculate_vocabulary_complexity(text),
            "pauses_count": 0,  # Cần audio analysis thực tế
            "filler_words": self._count_filler_words(text)
        }
    
    def _count_filler_words(self, text: str) -> List[str]:
        """Đếm filler words"""
        filler_words = ["um", "uh", "like", "you know", "actually", "basically"]
        found = []
        
        text_lower = text.lower()
        for filler in filler_words:
            if filler in text_lower:
                found.append(filler)
        
        return found