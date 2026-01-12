# Sử dụng Python bản ổn định
FROM python:3.10-slim

# Cài đặt FFmpeg
RUN apt-get update && apt-get install -y ffmpeg && rm -rf /var/lib/apt/lists/*

# Thiết lập thư mục làm việc
WORKDIR /app

# Copy file requirements và cài đặt thư viện
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ code vào container
COPY . .

# Chạy lệnh khởi động server
CMD ["uvicorn", "main:app", "--host", "0.0.0.0", "--port", "8001"]