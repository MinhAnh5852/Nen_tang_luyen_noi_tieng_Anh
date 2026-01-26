import os
import pika
import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from werkzeug.security import generate_password_hash
from database import db
from models.user import User, Feedback

user_bp = Blueprint("users", __name__)

# --- HÀM GỬI TIN NHẮN RABBITMQ (Đã tối ưu timeout) ---
def send_to_analytics(event_type, data=None):
    connection = None
    try:
        rabbitmq_host = os.getenv("RABBITMQ_HOST", "app-rabbitmq")
        rabbitmq_user = os.getenv("RABBITMQ_USER", "admin")
        rabbitmq_pass = os.getenv("RABBITMQ_PASS", "admin123")
        
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
        # Thêm socket_timeout để tránh treo API nếu RabbitMQ chưa sẵn sàng
        params = pika.ConnectionParameters(
            host=rabbitmq_host,
            credentials=credentials,
            socket_timeout=2
        )
        
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='analytics_queue', durable=True)
        
        message = {"event": event_type}
        if data: message.update(data)
            
        channel.basic_publish(
            exchange='',
            routing_key='analytics_queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2, content_type='application/json')
        )
    except Exception as e:
        print(f"!!! RabbitMQ Alert: {e}") # Không làm crash API nếu RabbitMQ lỗi
    finally:
        if connection and not connection.is_closed:
            connection.close()

# --- 1. LẤY DANH SÁCH USERS (Cho Dashboard Admin) ---
@user_bp.route("/all", methods=["GET"])
def get_all_users():
    try:
        users = User.query.all()
        result = []
        for u in users:
            # Đảm bảo trả về đúng các field mà Frontend đang gọi
            result.append({
                "id": u.id,
                "username": u.username or u.email.split('@')[0],
                "email": u.email,
                "role": str(u.role).lower(), # Trả về 'admin', 'learner', 'mentor'
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
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User không tồn tại"}), 404
        
        return jsonify({
            "id": user.id,
            "username": user.username or user.email.split('@')[0],
            "email": user.email,
            "role": str(user.role).lower()
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 3. ĐĂNG KÝ (Có tích hợp Analytics) ---
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
        u = User(
            email=email, 
            username=data.get("username") or email.split('@')[0],
            password=generate_password_hash(password), 
            role=(data.get("role") or "learner").lower()
        )
        db.session.add(u)
        db.session.commit()

        # Gửi dữ liệu sang Analytics Service qua RabbitMQ
        send_to_analytics("new_user_registered", {"email": email, "id": str(u.id)})
        
        return jsonify({"id": u.id, "message": "Tạo tài khoản thành công"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500