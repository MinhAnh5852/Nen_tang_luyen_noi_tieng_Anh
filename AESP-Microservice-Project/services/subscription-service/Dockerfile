# 1. Sử dụng Python 3.10-slim (Rất tốt)
FROM python:3.10-slim

# 2. Thiết lập thư mục làm việc
WORKDIR /app

# 3. Cài đặt thư viện hệ thống (Chỉ cần thiết nếu dùng mysql-client, 
# nhưng với PyMySQL bạn có thể bỏ qua bước này để image nhẹ hơn)
# Nếu sau này có dùng thư viện gì cần biên dịch thì hãy thêm lại GCC sau.

# 4. Copy và cài đặt thư viện Python trước (Tận dụng Cache)
COPY requirements.txt .
RUN pip install --no-cache-dir -r requirements.txt

# 5. Copy toàn bộ mã nguồn
COPY . .

# 6. Mở cổng 5001
EXPOSE 5001

# 7. Lệnh chạy ứng dụng
CMD ["python", "app.py"]