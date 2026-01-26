import os
from dotenv import load_dotenv

# Load các biến từ file .env nếu có (khi chạy local không docker)
load_dotenv()

class Config:
    # 1. Cấu hình Flask
    SECRET_KEY = os.getenv("SECRET_KEY", "subscription-secret-key-123")
    DEBUG = os.getenv("DEBUG", "True") == "True"

    # 2. Cấu hình Database (Kết nối đến mysql-db và subscription_db)
    DB_USER = os.getenv("DB_USER", "root")
    DB_PASSWORD = os.getenv("DB_PASSWORD", "root") # Nhớ khớp với mật khẩu ở User Service
    DB_HOST = os.getenv("DB_HOST", "mysql-db")
    DB_PORT = os.getenv("DB_PORT", "3306")
    DB_NAME = os.getenv("DB_NAME", "subscription_db")

    # Chuỗi kết nối SQLAlchemy cho PyMySQL
    SQLALCHEMY_DATABASE_URI = f"mysql+pymysql://{DB_USER}:{DB_PASSWORD}@{DB_HOST}:{DB_PORT}/{DB_NAME}"
    
    # 3. Tối ưu hóa kết nối
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    SQLALCHEMY_ENGINE_OPTIONS = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }

    # 4. JWT (Nếu cần xác thực Admin/User)
    JWT_SECRET_KEY = os.getenv("JWT_SECRET_KEY", "jwt-secret-key-456")