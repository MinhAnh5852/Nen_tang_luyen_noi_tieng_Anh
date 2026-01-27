import os
import pika
import json
import uuid  # Thêm uuid để đồng bộ ID
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from database import db
from models.user import User, Feedback

user_bp = Blueprint("users", __name__)

# --- HÀM GỬI TIN NHẮN RABBITMQ ---
def send_to_mq(event_type, data=None):
    connection = None
    try:
        # Sử dụng đúng tên service RabbitMQ trong Docker network
        rabbitmq_url = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@app-rabbitmq:5672/')
        params = pika.URLParameters(rabbitmq_url)
        params.socket_timeout = 2 
        
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        
        channel.queue_declare(queue='user_events', durable=True)
        
        message = {"event": event_type}
        if data: 
            message.update(data)
            
        channel.basic_publish(
            exchange='',
            routing_key='user_events',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2, content_type='application/json')
        )
        print(f">>> [MQ Success]: Event {event_type} sent to user_events")
    except Exception as e:
        # Chỉ in log cảnh báo, không làm crash luồng chính
        print(f"!!! RabbitMQ Warning (User Controller): {e}") 
    finally:
        if connection and not connection.is_closed:
            connection.close()

# --- 1. LẤY DANH SÁCH USERS ---
@user_bp.route("/all", methods=["GET"])
def get_all_users():
    try:
        users = User.query.all()
        result = []
        for u in users:
            result.append({
                "id": u.id,
                "username": u.username or u.email.split('@')[0],
                "email": u.email,
                "role": str(u.role).lower(),
                "status": str(u.status).lower() if u.status else "active",
                "package_name": u.package_name or 'Free'
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 2. LẤY THÔNG TIN CÁ NHÂN ---
@user_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    try:
        # Identity từ token thường là string của User ID
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User không tồn tại"}), 404
        
        return jsonify({
            "id": user.id,
            "username": user.username or user.email.split('@')[0],
            "email": user.email,
            "role": str(user.role).lower(),
            "package_name": user.package_name or 'Free'
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 3. ĐĂNG KÝ (Đồng bộ UUID và MQ) ---
@user_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True, silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    
    if not email or not password:
        return jsonify({"error": "Thiếu email hoặc mật khẩu"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email đã tồn tại"}), 409

    try:
        # Sử dụng UUID để thống nhất ID trên toàn hệ thống
        u = User(
            id=str(uuid.uuid4()), 
            email=email, 
            username=data.get("username") or email.split('@')[0],
            password=generate_password_hash(password), 
            role=(data.get("role") or "learner").lower(),
            status="active"
        )
        db.session.add(u)
        db.session.commit()

        # Gửi MQ không chặn (Async-like behavior)
        send_to_mq("USER_REGISTERED", {
            "user_id": str(u.id),
            "email": u.email,
            "username": u.username,
            "role": u.role
        })
        
        return jsonify({"id": u.id, "message": "Tạo tài khoản thành công"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500