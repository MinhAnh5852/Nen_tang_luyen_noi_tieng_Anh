FROM python:3.9-slim

# Thiết lập thư mục làm việc
WORKDIR /app

# Cài đặt các thư viện hệ thống cần thiết cho MySQL (MariaDB client)
# Thêm 'pkg-config' để pip có thể tìm thấy thư viện MariaDB khi cài pymysql/mysqlclient
RUN apt-get update && apt-get install -y \
    libmariadb-dev \
    gcc \
    pkg-config \
    && rm -rf /var/lib/apt/lists/*

# Copy file requirements trước để tận dụng Docker Cache
COPY requirements.txt .

# Cài đặt các thư viện Python
RUN pip install --no-cache-dir -r requirements.txt

# Copy toàn bộ mã nguồn vào container
COPY . .

# Môi trường Python không đệm (in log ngay lập tức)
ENV PYTHONUNBUFFERED=1

# Cổng chạy của Payment Service
EXPOSE 5004

# Lệnh khởi chạy
CMD ["python", "app.py"]