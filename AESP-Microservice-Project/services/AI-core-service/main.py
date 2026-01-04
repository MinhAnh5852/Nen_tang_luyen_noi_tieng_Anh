import os
import whisper
from fastapi import FastAPI, UploadFile, File, Depends
from groq import Groq
from sqlalchemy.orm import Session
import models, database # Dựa trên sơ đồ xdpm bạn đã vẽ

app = FastAPI()

# 1. Tải model Whisper về máy (chỉ chạy lần đầu, hoàn toàn free)
model_whisper = whisper.load_model("base") 

# 2. Cấu hình Groq API (Dùng Llama 3 - Miễn phí)
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
        f.write(file.file.read())

    # BƯỚC 1: CHUYỂN AUDIO SANG TEXT (Chạy trên máy bạn - FREE)
    result = model_whisper.transcribe(temp_file)
    user_text = result['text']

    # BƯỚC 2: GỬI TEXT SANG GROQ ĐỂ PHÂN TÍCH (FREE & NHANH)
    chat_completion = client_groq.chat.completions.create(
        messages=[
            {
                "role": "system", 
                "content": "Bạn là chuyên gia tiếng Anh. Hãy trả về kết quả JSON: {grammar_score: int, feedback: string}"
            },
            {"role": "user", "content": f"Hãy sửa lỗi và chấm điểm câu này: {user_text}"}
        ],
        model="llama3-8b-8192", # Model Llama 3 cực mạnh của Meta
    )
    
    # Giả định lấy kết quả từ AI
    ai_feedback = chat_completion.choices[0].message.content

    # BƯỚC 3: LƯU VÀO DATABASE xdpm
    new_session = models.Session(
        Learner_ID=learner_id,
        Topic_ID=topic_id,
        Transcript=user_text,
        AI_Grammar_Score=80, # Trích xuất từ ai_feedback
        AI_Pronunciation_Score=75 # Bạn có thể dùng Librosa để tính thêm
    )
    db.add(new_session)
    db.commit()

    os.remove(temp_file) # Xóa file tạm
    return {"transcript": user_text, "ai_feedback": ai_feedback}