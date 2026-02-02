from groq import Groq
import os
import json
from dotenv import load_dotenv

# Load biến môi trường
load_dotenv()

# Lấy API Key
client = Groq(api_key=os.environ.get("GROQ_API_KEY"))

def analyze_speech(user_text, topic):
    """
    Gửi văn bản người dùng đến Groq AI để nhận phản hồi và đánh giá.
    """
    system_prompt = f"""
    You are an elite English speaking partner and teacher. 
    Topic of conversation: {topic}.
    Your tasks:
    1. Respond naturally to the student's statement in 1-2 sentences to keep the conversation going.
    2. Provide a 'correction' if there are grammar or vocabulary mistakes.
    3. Provide an 'accuracy' score from 0 to 100 based on their English level.
    
    You MUST return the response in JSON format:
    {{
        "reply": "your response in English",
        "correction": "grammar correction or 'Perfect' if no mistakes",
        "accuracy": 85
    }}
    """
    try:
        chat_completion = client.chat.completions.create(
            messages=[
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_text}
            ],
            model="llama-3.3-70b-versatile",
            response_format={"type": "json_object"}
        )
        # Chuyển đổi chuỗi JSON từ AI thành Dictionary trong Python
        return json.loads(chat_completion.choices[0].message.content)
    except Exception as e:
        print(f"Error calling Groq API: {e}")
        return {"error": str(e)}