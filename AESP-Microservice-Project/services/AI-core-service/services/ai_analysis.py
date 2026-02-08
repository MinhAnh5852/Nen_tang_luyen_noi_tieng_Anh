from groq import Groq
import os
import json
from dotenv import load_dotenv

# 1. Load biến môi trường
load_dotenv()

# 2. Khởi tạo client với cơ chế kiểm tra Key
api_key = os.environ.get("GROQ_API_KEY")
if not api_key:
    print("🔥 CRITICAL WARNING: GROQ_API_KEY is missing in environment variables!")

client = Groq(api_key=api_key)

def analyze_speech(user_text, topic):
    """
    Gửi văn bản người dùng đến Groq AI để nhận phản hồi và đánh giá.
    """
    # System Prompt được tối ưu để ép AI chỉ trả về đúng cấu trúc JSON
    system_prompt = f"""
    You are an elite English speaking partner and teacher. 
    Topic: {topic}.
    Your tasks:
    1. Respond naturally in 1-2 sentences to keep the conversation going.
    2. Provide a 'correction' for any grammar/vocabulary mistakes.
    3. Provide an 'accuracy' score (0-100).
    
    CRITICAL: You MUST return ONLY a JSON object. No intro, no outro.
    Format:
    {{
        "reply": "your response",
        "correction": "correction or 'Perfect'",
        "accuracy": 85
    }}
    """
    
    try:
        # Sử dụng model llama3-8b-8192 để mượt mà hơn cho tài khoản Free (ít bị Rate Limit hơn bản 70b)
        # Nếu Bảo muốn dùng bản mạnh nhất thì đổi lại thành "llama-3.3-70b-versatile"
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            model="llama-3.1-8b-instant",
            response_format={"type": "json_object"},
            temperature=0.7,
            max_tokens=512
        )
        
        # Lấy nội dung thô từ AI
        raw_content = chat_completion.choices[0].message.content
        
        # Debug: In ra để Bảo theo dõi trong Docker logs
        print(f"--- AI Response for Topic [{topic}]: {raw_content}")
        
        # 3. Chuyển đổi an toàn sang Dictionary
        return json.loads(raw_content)

    except json.JSONDecodeError as e:
        print(f"🔥 Lỗi định dạng JSON: {e}. Nội dung AI trả về: {raw_content}")
        return {
            "reply": "I'm sorry, I had a technical glitch. Could you repeat that?",
            "correction": "System Error: Invalid JSON",
            "accuracy": 0
        }
    except Exception as e:
        # Nếu lỗi do Rate Limit (gọi quá nhiều) hoặc mạng, trả về lỗi thay vì làm sập cả app
        error_msg = str(e)
        print(f"🔥 Error calling Groq API: {error_msg}")
        
        if "429" in error_msg:
            return {"error": "AI is busy (Rate Limit). Please wait 1 minute."}
        
        return {"error": error_msg}