import os
from dotenv import load_dotenv

load_dotenv()

class Config:
    # Đã sửa: Trỏ mặc định sang payment_db riêng biệt
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "DATABASE_URL", 
        "mysql+pymysql://root:root@user-db:3306/payment_db"
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False
    
    # URL gọi nội bộ sang User Service (Port 5000) để nâng cấp gói
    # Giữ nguyên vì đây là đường dẫn gọi API giữa các service
    USER_SERVICE_INTERNAL_URL = os.getenv(
        "USER_SERVICE_URL",
        "http://user-service:5000/internal/upgrade-package"
    )