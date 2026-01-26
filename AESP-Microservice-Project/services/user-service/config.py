import os
from datetime import timedelta
from dotenv import load_dotenv

# Tải các biến môi trường từ file .env
load_dotenv()

class Config:
    # --- CẤU HÌNH DATABASE (Đã chuyển sang MySQL) ---
    # mysql+pymysql://root:root@user-db:3306/user_db
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://root:root@user-db:3306/user_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # Tối ưu kết nối MySQL để tránh lỗi "gone away"
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }

    # --- CẤU HÌNH JWT (Bảo mật cho Admin/User) ---
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "AESP_SUPER_SECRET_KEY_2026")
    JWT_ACCESS_TOKEN_EXPIRES = timedelta(hours=24) # Token có hạn 1 ngày

    # --- CẤU HÌNH RABBITMQ (Cho Analytics) ---
    RABBITMQ_HOST = os.getenv("RABBITMQ_HOST", "app-rabbitmq")
    RABBITMQ_USER = os.getenv("RABBITMQ_USER", "admin")
    RABBITMQ_PASS = os.getenv("RABBITMQ_PASS", "admin123")

    # --- CÁC CẤU HÌNH KHÁC ---
    DEBUG = os.getenv("FLASK_DEBUG", "True") == "True"
    SECRET_KEY = os.getenv("SECRET_KEY", "flask_secret_key_random")