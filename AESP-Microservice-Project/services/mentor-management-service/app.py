import os
import threading
from flask import Flask, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
from database import db, init_db
from controllers.mentor_controller import mentor_bp
from mq_worker import start_worker  # ✅ Import worker để chạy ngầm

# 1. Load biến môi trường
load_dotenv()

def create_app():
    app = Flask(__name__)

    # --- CẤU HÌNH CORS ---
    CORS(app, resources={r"/*": {"origins": "*", "methods": ["GET", "POST", "PUT", "DELETE", "OPTIONS"],
        "allow_headers": ["Content-Type", "Authorization", "Accept"] }})

    # --- CẤU HÌNH DATABASE ---
    db_url = os.environ.get('DATABASE_URL')
    if not db_url:
        # Fallback về user_db vì anh em mình đã thống nhất dùng chung DB cho đồng bộ
        db_url = 'mysql+pymysql://root:root@user-db:3306/user_db?charset=utf8mb4'
        print(f"⚠️ Cảnh báo: Dùng link DB mặc định: {db_url}")

    app.config['SQLALCHEMY_DATABASE_URI'] = db_url
    app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

    # 2. Khởi tạo DB
    init_db(app)

    # 3. Đăng ký API Blueprint
    app.register_blueprint(mentor_bp, url_prefix='/api/mentors')

    # 4. CHẠY WORKER TRONG LUỒNG RIÊNG (THREAD)
    # daemon=True đảm bảo khi tắt Flask thì Worker cũng tắt theo
    print("🚀 Đang khởi chạy Mentor Worker chạy ngầm (RabbitMQ)...")
    worker_thread = threading.Thread(target=start_worker, daemon=True)
    worker_thread.start()

    # 5. Route kiểm tra nhanh
    @app.route('/')
    def index():
        return jsonify({
            "status": "success", 
            "message": "Mentor Service is running!",
            "worker_alive": worker_thread.is_alive() # Kiểm tra xem worker còn sống không
        }), 200

    return app

app = create_app()

if __name__ == "__main__":
    # Chạy server cổng 5002
    print("🚀 Mentor Service đang chạy tại: http://0.0.0.0:5002")
    app.run(host="0.0.0.0", port=5002, debug=True, use_reloader=False) 
    # Lưu ý: use_reloader=False để tránh khởi chạy 2 lần Worker khi ở mode Debug