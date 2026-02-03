# app.py
from flask import Flask, jsonify
from flask_cors import CORS # Thư viện giúp Frontend gọi được API
from dotenv import load_dotenv
import os
from database import db, init_db
from controllers.mentor_controller import mentor_bp

# 1. Load biến môi trường từ file .env
load_dotenv()

app = Flask(__name__)

# --- CẤU HÌNH CORS (QUAN TRỌNG) ---
# Cho phép mọi tên miền (origins="*") gọi vào API để tránh lỗi chặn kết nối
CORS(app, resources={r"/*": {"origins": "*"}})

# 2. Cấu hình Database
# Lấy link từ biến môi trường, nếu không có thì dùng link mặc định (để tránh lỗi crash)
db_url = os.environ.get('DATABASE_URL')
if not db_url:
    # Fallback: Mặc định kết nối localhost cổng 3307 (dựa theo log cũ của bạn)
    # Bạn nhớ sửa 'root' và password nếu khác
    db_url = 'mysql+pymysql://root:@localhost:3307/mentor_management_db'
    print(f"⚠️  Canh bao: Khong tim thay DATABASE_URL trong .env, dung mac dinh: {db_url}")

app.config['SQLALCHEMY_DATABASE_URI'] = db_url
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 3. Khởi tạo DB
init_db(app)

# 4. Đăng ký API Blueprint
app.register_blueprint(mentor_bp, url_prefix='/api/mentors')

# 5. Route kiểm tra nhanh (Ping)
@app.route('/')
def index():
    return jsonify({
        "status": "success", 
        "message": "Mentor Service (Port 5002) is running!", 
        "database": db_url.split('@')[-1] # Hiển thị tên DB đang kết nối
    }), 200

if __name__ == "__main__":
    # Chạy server
    print("🚀 Mentor Service dang chay tai: http://127.0.0.1:5002")
    app.run(host="0.0.0.0", port=5002, debug=True)