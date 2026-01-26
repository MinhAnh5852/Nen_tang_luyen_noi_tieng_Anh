import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Khởi tạo đối tượng SQLAlchemy
db = SQLAlchemy()

def get_database_url():
    """
    Lấy URL database cho Subscription Service.
    Mặc định kết nối tới database 'subscription_db'.
    """
    url = os.getenv("DATABASE_URL")
    if not url:
        # CHÚ Ý: Thay user_db thành subscription_db
        # Giữ nguyên pymysql giống User Service để tránh lỗi thư viện
        return "mysql+pymysql://root:123456@mysql-db:3306/subscription_db"
    
    # Chuẩn hóa URL nếu lấy từ biến môi trường
    if url.startswith("mysql://"):
         url = url.replace("mysql://", "mysql+pymysql://", 1)
         
    return url

def init_db(app):
    """
    Cấu hình và khởi tạo database cho Subscription App
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Chống lỗi treo kết nối MySQL
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }
    
    db.init_app(app)

# Dành cho các scripts chạy độc lập bên ngoài Flask
engine = create_engine(get_database_url(), pool_recycle=280, pool_pre_ping=True)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))