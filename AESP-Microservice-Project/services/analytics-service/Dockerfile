# 1. Chọn image Python làm nền
FROM python:3.10-slim

# 2. Tạo thư mục làm việc trong container
WORKDIR /app

# 3. Copy file requirements trước (tối ưu cache)
COPY requirements.txt .

# 4. Cài thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy toàn bộ source code vào container
COPY . .

# 6. Lệnh chạy service
CMD ["python", "app.py"]
