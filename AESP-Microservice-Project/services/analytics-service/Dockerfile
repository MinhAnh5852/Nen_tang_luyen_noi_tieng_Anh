FROM python:3.9-slim

WORKDIR /app

# Chỉ cài đặt các thư viện cần thiết cho việc build nếu thực sự cần
# Với pymysql thường không cần gcc
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 5003

# Khởi chạy đồng thời Worker và API
CMD ["sh", "-c", "python mq_worker.py & python app.py"]  