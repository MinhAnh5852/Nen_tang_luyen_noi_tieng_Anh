import os
import time
from flask import Flask
from flask_cors import CORS
from flask_jwt_extended import JWTManager  # THÊM DÒNG NÀY
from database import db
from config import Config
from controllers.auth_controller import auth_bp
from controllers.user_controller import user_bp
from controllers.internal_controller import internal_bp
from sqlalchemy.exc import OperationalError

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # Cấu hình JWT (Bắt buộc để chạy được hàm get_current_user)
    app.config["JWT_SECRET_KEY"] = os.getenv("JWT_SECRET_KEY", "your-secret-key-123") 
    app.config["JWT_ACCESS_TOKEN_EXPIRES"] = 86400  # Token hết hạn sau 24h
    
    jwt = JWTManager(app) # Khởi tạo JWTManager
    db.init_app(app)

    # Cho phép CORS để Frontend gọi API không bị chặn
    CORS(app)

    # Đăng ký Blueprint không prefix để khớp với cấu hình Nginx Gateway
    app.register_blueprint(auth_bp, url_prefix='') 
    app.register_blueprint(user_bp, url_prefix='') 
    app.register_blueprint(internal_bp, url_prefix='')

    # Cơ chế Retry kết nối DB (Tránh lỗi sập khi Database khởi động chậm)
    with app.app_context():
        retries = 5
        while retries > 0:
            try:
                db.create_all()
                print("User Database connected and tables created!")
                break
            except OperationalError:
                retries -= 1
                print(f"Waiting for User DB... ({retries} retries left)")
                time.sleep(5)
    
    return app

app = create_app()

if __name__ == "__main__":
    # Chạy trên cổng 5000 bên trong container
    app.run(host="0.0.0.0", port=5000)