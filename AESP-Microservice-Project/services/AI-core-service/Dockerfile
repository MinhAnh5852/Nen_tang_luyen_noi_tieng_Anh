# Sử dụng Python bản ổn định
FROM python:3.10-slim

# Cài đặt FFmpeg (cho Whisper AI)
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /app

COPY requirements.txt .

# Danh sách này bao gồm: FastAPI, Database, AI, và Groq
RUN pip install --no-cache-dir fastapi uvicorn sqlalchemy mysql-connector-python groq python-dotenv python-multipart requests openai-whisper

# Copy toàn bộ code vào container
COPY . .

# Chạy lệnh khởi động server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]