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
def send_mq_message(message):
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
        print(f">>> [MQ Success]: Đã gửi sự kiện {message.get('event')}")
    except Exception as e:
        print(f">>> [RabbitMQ Error]: {e}")

# --- 1. ĐĂNG KÝ (Cập nhật: Gửi đầy đủ thông tin Mentor) ---
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
            password=generate_password_hash(password),
            role=role,
            status="active"
        )
        db.session.add(new_user)
        db.session.commit()

        # FIX: Gửi đầy đủ username cho Mentor Service nhận diện
        send_mq_message({
            "event": "USER_REGISTERED",
            "user_id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role
        })

        return jsonify({"message": "Đăng ký thành công", "user_id": new_user.id}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi lưu Database: {str(e)}"}), 500

# --- 6. CẬP NHẬT ROLE (Fix: Tự tạo Profile nếu đổi lên Mentor) ---
@auth_bp.route("/update-role", methods=["POST"])
def update_role():
    data = request.get_json()
    try:
        user = User.query.get(data.get('id'))
        if user:
            old_role = user.role
            new_role = data.get('role').lower()
            
            user.username = data.get('username')
            user.role = new_role
            
            new_password = data.get('password')
            if new_password and str(new_password).strip() != "":
                user.password = generate_password_hash(new_password)
            
            db.session.commit()

            # Nếu nâng cấp lên Mentor, tự động tạo Profile chờ duyệt
            if old_role != 'mentor' and new_role == 'mentor':
                send_mq_message({
                    "event": "USER_REGISTERED",
                    "user_id": user.id,
                    "username": user.username,
                    "email": user.email,
                    "role": "mentor"
                })

            return jsonify({"message": "Cập nhật thành công"}), 200
        return jsonify({"message": "User không tồn tại"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi cập nhật: {str(e)}"}), 500

# --- 7. ĐĂNG NHẬP QUA FIREBASE ---
@auth_bp.route("/login-firebase", methods=["POST"])
def login_firebase():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    username = data.get("username")

    if not email:
        return jsonify({"error": "Thiếu email từ Firebase"}), 400

    try:
        user = User.query.filter_by(email=email).first()
        is_new = False

        if not user:
            is_new = True
            user = User(
                id=str(uuid.uuid4()),
                username=username,
                email=email,
                password="FIREBASE_AUTHENTICATED",
                role="learner",
                status="active"
            )
            db.session.add(user)
            db.session.commit()

        token = create_access_token(identity=str(user.id))

        # Nếu là người mới đăng nhập Google, gửi tin nhắn đồng bộ các service
        if is_new:
            send_mq_message({
                "event": "USER_REGISTERED",
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role
            })

        return jsonify({
            "token": token,
            "user": {"id": user.id, "email": user.email, "role": user.role, "username": user.username}
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Lỗi đồng bộ Firebase: {str(e)}"}), 500

# --- GIỮ NGUYÊN CÁC ROUTE CÒN LẠI ---
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    try:
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({"error": "Email hoặc mật khẩu không chính xác"}), 401
        token = create_access_token(identity=str(user.id))
        return jsonify({"token": token, "user": {"id": user.id, "email": user.email, "role": user.role, "username": user.username}}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@auth_bp.route("/all", methods=["GET"])
def get_all_users():
    users = User.query.all()
    return jsonify([{"id": u.id, "username": u.username, "email": u.email, "role": u.role, "status": u.status} for u in users]), 200