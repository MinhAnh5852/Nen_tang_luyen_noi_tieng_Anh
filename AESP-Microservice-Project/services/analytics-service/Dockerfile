FROM python:3.9-slim

WORKDIR /app

# Cài đặt curl để có thể kiểm tra healthcheck nếu cần
RUN apt-get update && apt-get install -y curl && rm -rf /var/lib/apt/lists/*

COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

COPY . .

ENV PYTHONUNBUFFERED=1

EXPOSE 5003

# Khởi chạy đồng thời Worker và API
# Lưu ý: Đảm bảo mq_worker.py có logic retry kết nối RabbitMQ 
# để tránh việc container bị sập khi RabbitMQ khởi động chậm hơn.
CMD ["sh", "-c", "python mq_worker.py & python app.py"]