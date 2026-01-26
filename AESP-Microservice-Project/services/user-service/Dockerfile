FROM python:3.10-slim

# 1. Cài system dependencies (Chỉ giữ lại những cái thực sự cần)
# Pymysql không cần mysqlclient-dev nên mình có thể bỏ bớt để nhẹ image
RUN apt-get update && apt-get install -y \
    curl \
    && rm -rf /var/lib/apt/lists/*

# 2. Thiết lập thư mục làm việc
WORKDIR /app

# 3. Copy requirements và cài đặt (Tận dụng Layer Caching)
COPY requirements.txt .
RUN pip install --no-cache-dir --upgrade pip \
    && pip install --no-cache-dir -r requirements.txt

# 4. Copy toàn bộ source code vào container
COPY . .

# 5. Mở cổng 5000 cho Flask
EXPOSE 5000

# 6. Chạy bằng Gunicorn
# --workers 4: Giúp xử lý nhiều yêu cầu cùng lúc (tốt cho Admin Dashboard)
# --timeout 120: Tránh lỗi timeout nếu database phản hồi chậm lúc mới khởi động
CMD ["gunicorn", "--bind", "0.0.0.0:5000", "--workers", "4", "--timeout", "120", "app:app"]