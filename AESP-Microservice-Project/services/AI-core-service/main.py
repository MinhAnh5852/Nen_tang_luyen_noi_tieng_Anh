import os
import whisper
from fastapi import FastAPI, UploadFile, File, Depends
from groq import Groq
from sqlalchemy.orm import Session
import models, database 
from dotenv import load_dotenv

load_dotenv()

app = FastAPI()

#Tải model Whisper về máy
model_whisper = whisper.load_model("base") 

#Cấu hình Groq API
client_groq = Groq(api_key="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")

@app.post("/ai-core/analyze")
async def analyze_speaking(
    learner_id: int, 
    topic_id: int, 
    file: UploadFile = File(...),
    db: Session = Depends(database.get_db)
):
    # LƯU FILE TẠM
    temp_file = f"temp_{file.filename}"
    with open(temp_file, "wb") as f:
        f.write(await file.read())

    #CHUYỂN AUDIO SANG TEXT
    result = model_whisper.transcribe(temp_file)
    user_text = result['text']

    #GỬI TEXT SANG GROQ ĐỂ PHÂN TÍCH 
    chat_completion = client_groq.chat.completions.create(
        messages=[
            {
                "role": "system", 
                "content": "Bạn là chuyên gia tiếng Anh. Hãy trả về kết quả JSON: {grammar_score: int, feedback: string}"
            },
            {"role": "user", "content": f"Hãy sửa lỗi và chấm điểm câu này: {user_text}"}
        ],
        model="llama-3.1-8b-instant", # Model Llama 3 cực mạnh của Meta
    )
    
    # Giả định lấy kết quả từ AI
    ai_feedback = chat_completion.choices[0].message.content

    #LƯU VÀO DATABASE xdpm
    new_session = models.Session(
        Learner_ID=learner_id,
        Topic_ID=topic_id,
        Transcript=user_text,
        AI_Grammar_Score=80, # Trích xuất từ ai_feedback
        AI_Pronunciation_Score=75 
    )
    db.add(new_session)
    db.commit()

    os.remove(temp_file) # Xóa file tạm
    return {"transcript": user_text, "ai_feedback": ai_feedback}