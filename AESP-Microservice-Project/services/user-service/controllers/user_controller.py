import os
import pika
import json
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity # THÊM DÒNG NÀY
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from database import db
from models.user import User, Feedback

user_bp = Blueprint("users", __name__)

# --- HÀM BỔ TRỢ: GỬI TIN NHẮN SANG RABBITMQ ---
def send_to_analytics(event_type, data=None):
    connection = None
    try:
        rabbitmq_host = os.getenv("RABBITMQ_HOST", "app-rabbitmq")
        rabbitmq_user = os.getenv("RABBITMQ_USER", "admin")
        rabbitmq_pass = os.getenv("RABBITMQ_PASS", "admin123")
        
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
        params = pika.ConnectionParameters(
            host=rabbitmq_host,
            credentials=credentials,
            connection_attempts=5,
            retry_delay=5,
            heartbeat=600
        )
        
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        channel.queue_declare(queue='analytics_queue', durable=True)
        
        message = {"event": event_type}
        if data:
            message.update(data)
            
        channel.basic_publish(
            exchange='',
            routing_key='analytics_queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(delivery_mode=2, content_type='application/json')
        )
        print(f" [x] Sent to RabbitMQ: {event_type}")
        
    except Exception as e:
        print(f" !!! Lỗi gửi tin nhắn RabbitMQ: {e}")
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
                "email": u.email,
                "role": str(u.role),
                "status": u.status,
                "package_name": getattr(u, 'package_name', 'Free')
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 2. LẤY THÔNG TIN CÁ NHÂN (FIXED) ---
@user_bp.route("/me", methods=["GET"])
@jwt_required()
def get_current_user():
    try:
        user_id = get_jwt_identity() # Lấy ID từ Token
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User không tồn tại"}), 404
        
        # Trả về dữ liệu khớp với Model User của bạn
        return jsonify({
            "id": user.id,
            "username": user.username or user.email.split('@')[0], # Tránh lỗi nếu username null
            "email": user.email,
            "role": str(user.role) 
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 3. ĐĂNG KÝ ---
@user_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True, silent=True) or {}
    
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    username = data.get("username") or email.split('@')[0] # Thêm username
    role = (data.get("role") or "learner").strip().lower()

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    try:
        # Tạo user mới kèm theo username để tránh lỗi Profile
        u = User(
            email=email, 
            username=username,
            password=generate_password_hash(password), 
            role=role
        )
        db.session.add(u)
        db.session.commit()

        send_to_analytics("new_user", {"email": email, "id": str(u.id)})
        return jsonify({"id": u.id, "message": "User created"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500