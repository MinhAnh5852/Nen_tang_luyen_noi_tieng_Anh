import os
import pika
import json
import uuid
from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash, check_password_hash
from database import db
from models.user import User
from flask_jwt_extended import create_access_token

auth_bp = Blueprint("auth", __name__)

# --- HÀM BỔ TRỢ: GỬI TIN NHẮN ĐẾN RABBITMQ ---
def send_mq_message(routing_key, message):
    try:
        url = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672/')
        params = pika.URLParameters(url)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='user_events', durable=True)
        
        channel.basic_publish(
            exchange='',
            routing_key='user_events',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
    except Exception as e:
        print(f">>> [RabbitMQ Error]: {e}")

# --- 1. ĐĂNG KÝ (Admin thêm User hoặc User tự đăng ký) ---
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username")
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    role = (data.get("role") or "learner").lower()

    if not email or not password:
        return jsonify({"message": "Email và mật khẩu là bắt buộc"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email này đã được đăng ký!"}), 409

    try:
        new_user = User(
            id=str(uuid.uuid4()),
            username=username,
            email=email,
            # BẮT BUỘC HASH MẬT KHẨU KHI TẠO MỚI
            password=generate_password_hash(password),
            role=role,
            status="active"
        )
        db.session.add(new_user)
        db.session.commit()

        send_mq_message('user_events', {
            "event": "USER_REGISTERED",
            "user_id": new_user.id,
            "email": new_user.email,
            "role": new_user.role
        })

        return jsonify({"message": "Đăng ký thành công", "user_id": new_user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi lưu Database: {str(e)}"}), 500

# --- 2. ĐĂNG NHẬP (Sử dụng check_password_hash) ---
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    try:
        user = User.query.filter_by(email=email).first()
        
        # Kiểm tra user tồn tại và mật khẩu có khớp không
        if not user or not check_password_hash(user.password, password):
            return jsonify({"error": "Email hoặc mật khẩu không chính xác"}), 401
            
        if user.status in ["inactive", "disabled"]:
            return jsonify({"error": "Tài khoản đang bị khóa"}), 403

        token = create_access_token(identity=str(user.id))
        return jsonify({
            "token": token,
            "user": {"id": user.id, "email": user.email, "role": user.role, "username": user.username}
        }), 200
    except Exception as e:
        return jsonify({"error": f"Lỗi hệ thống: {str(e)}"}), 500

# --- 3. LẤY TOÀN BỘ USER ---
@auth_bp.route("/all", methods=["GET"])
def get_all_users():
    users = User.query.all()
    output = [{"id": u.id, "username": u.username, "email": u.email, "role": u.role, "status": u.status} for u in users]
    return jsonify(output), 200

# --- 4. XÓA NGƯỜI DÙNG ---
@auth_bp.route("/delete/<id>", methods=["DELETE"])
def delete_user(id):
    try:
        user = User.query.get(id)
        if not user:
            return jsonify({"message": "Không tìm thấy người dùng"}), 404
        
        user_email = user.email
        db.session.delete(user)
        db.session.commit()

        send_mq_message('user_events', {
            "event": "USER_DELETED",
            "user_id": id,
            "email": user_email
        })

        return jsonify({"message": "Xóa thành công"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": "Lỗi xóa dữ liệu"}), 500

# --- 5. CẬP NHẬT TRẠNG THÁI ---
@auth_bp.route("/update-status", methods=["POST"])
def update_status():
    data = request.get_json()
    try:
        user = User.query.get(data.get('id'))
        if user:
            user.status = data.get('status')
            db.session.commit()
            return jsonify({"message": "Cập nhật thành công"}), 200
        return jsonify({"message": "User không tồn tại"}), 404
    except Exception as e:
        return jsonify({"message": "Lỗi cập nhật"}), 500

# --- 6. CẬP NHẬT ROLE & MẬT KHẨU (Nếu có) ---
@auth_bp.route("/update-role", methods=["POST"])
def update_role():
    data = request.get_json()
    try:
        user = User.query.get(data.get('id'))
        if user:
            user.username = data.get('username')
            user.role = data.get('role')
            
            # KIỂM TRA NẾU ADMIN CÓ NHẬP MẬT KHẨU MỚI THÌ MỚI CẬP NHẬT
            new_password = data.get('password')
            if new_password and str(new_password).strip() != "":
                user.password = generate_password_hash(new_password)
            
            db.session.commit()
            return jsonify({"message": "Cập nhật thành công"}), 200
        return jsonify({"message": "User không tồn tại"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi cập nhật: {str(e)}"}), 500
    # --- 7. ĐĂNG NHẬP QUA FIREBASE (Cầu nối liên kết) ---
@auth_bp.route("/login-firebase", methods=["POST"])
def login_firebase():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    username = data.get("username")

    if not email:
        return jsonify({"error": "Thiếu email từ Firebase"}), 400

    try:
        # 1. Tìm xem user này đã tồn tại trong MySQL chưa
        user = User.query.filter_by(email=email).first()

        if not user:
            # 2. Nếu chưa có (người mới dùng Google Login lần đầu) -> Tự động tạo record trong MySQL
            user = User(
                id=str(uuid.uuid4()),
                username=username,
                email=email,
                password="FIREBASE_AUTHENTICATED", # Đánh dấu để biết user này thuộc quản lý của Firebase
                role="learner", # Mặc định là học viên
                status="active"
            )
            db.session.add(user)
            db.session.commit()
            
            # [MQ EVENT]: Thông báo có người dùng mới từ Firebase
            send_mq_message('user_events', {
                "event": "USER_REGISTERED_VIA_FIREBASE",
                "email": email,
                "role": "learner"
            })

        # 3. Luôn tạo Token của riêng hệ thống mình dựa trên thông tin trong MySQL
        # Điều này giúp Admin có thể thay đổi Role của họ trong MySQL và nó có hiệu lực ngay
        token = create_access_token(identity=str(user.id))
        
        return jsonify({
            "token": token,
            "user": {
                "id": user.id,
                "email": user.email,
                "role": user.role,
                "username": user.username
            }
        }), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Lỗi đồng bộ Firebase: {str(e)}"}), 500