import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from database import db, init_db
from config import Config
from controllers.auth_controller import auth_bp
from controllers.user_controller import user_bp
from controllers.internal_controller import internal_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    init_db(app)
    
    with app.app_context():
        try:
            from models.user import User, Feedback 
            db.create_all()
            print(">>> [MySQL] Database đã sẵn sàng!")
        except Exception as e:
            print(f">>> [MySQL] Lỗi khởi tạo: {e}")
    
    CORS(app, resources={r"/*": {"origins": "*"}})
    jwt = JWTManager(app)

    # ĐĂNG KÝ BLUEPRINT: Sửa prefix để khớp với Nginx
    # Nếu Nginx config là location /api/users/ { proxy_pass ... }
    # Thì các route trong auth_bp sẽ bắt đầu bằng /auth/...
    app.register_blueprint(auth_bp, url_prefix='/auth') 
    app.register_blueprint(user_bp, url_prefix='/profile')
    app.register_blueprint(internal_bp, url_prefix='/internal')

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "user-service"}), 200

    # ROUTE QUAN TRỌNG: Phục vụ trang Admin Dashboard
    # Trình duyệt gọi: /api/users/all -> Nginx -> /all
    @app.get("/all")
    def get_all_users_direct():
        try:
            from sqlalchemy import text
            # Thêm username và status vào câu lệnh SQL
            sql = text("SELECT id, username, email, role, status FROM users ORDER BY id DESC")
            result = db.session.execute(sql)
            users = [dict(r._mapping) for r in result]
            return jsonify(users), 200
        except Exception as e:
            print(f"Lỗi truy vấn SQL: {e}")
            return jsonify({"error": str(e)}), 500

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)