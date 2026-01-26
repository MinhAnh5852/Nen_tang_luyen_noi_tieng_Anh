import os
from flask_sqlalchemy import SQLAlchemy
from sqlalchemy import create_engine
from sqlalchemy.orm import sessionmaker, scoped_session

# Khởi tạo đối tượng SQLAlchemy cho Flask
db = SQLAlchemy()

def get_database_url():
    """
    Lấy URL database từ biến môi trường.
    Nếu không có, mặc định dùng chuỗi kết nối MySQL cho Docker.
    """
    url = os.getenv("DATABASE_URL")
    if not url:
        # Định dạng: mysql+pymysql://user:password@host:port/dbname
        return "mysql+pymysql://root:root@user-db:3306/user_db"
    
    # Đảm bảo nếu url truyền từ .env dùng postgresql:// thì sửa lại cho mysql
    if url.startswith("postgresql://"):
        url = url.replace("postgresql://", "mysql+pymysql://", 1)
    elif url.startswith("mysql://"):
         url = url.replace("mysql://", "mysql+pymysql://", 1)
         
    return url

def init_db(app):
    """
    Cấu hình và khởi tạo database cho Flask app
    """
    app.config['SQLALCHEMY_DATABASE_URI'] = get_database_url()
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
    
    # Tăng cường độ ổn định cho kết nối MySQL (tránh lỗi 'MySQL server has gone away')
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
    }
    
    db.init_app(app)

# Tạo Session thủ công (nếu Trọng cần dùng ngoài Flask context hoặc cho scripts)
engine = create_engine(get_database_url(), pool_recycle=280, pool_pre_ping=True)
SessionLocal = scoped_session(sessionmaker(autocommit=False, autoflush=False, bind=engine))