import os
import pika
import json
from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash
from database import db
from models.user import User, Feedback

user_bp = Blueprint("users", __name__)

# --- HÀM BỔ TRỢ: GỬI TIN NHẮN SANG RABBITMQ (ĐÃ SỬA LỖI AUTH) ---
def send_to_analytics(event_type, data=None):
    connection = None
    try:
        # 1. Lấy cấu hình từ môi trường (khớp với Docker Compose)
        rabbitmq_host = os.getenv("RABBITMQ_HOST", "app-rabbitmq")
        rabbitmq_user = os.getenv("RABBITMQ_USER", "admin")
        rabbitmq_pass = os.getenv("RABBITMQ_PASS", "admin123")
        
        # 2. Thiết lập thông số xác thực (QUAN TRỌNG ĐỂ HẾT LỖI LOGIN REFUSED)
        credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
        
        params = pika.ConnectionParameters(
            host=rabbitmq_host,
            credentials=credentials, # Thêm dòng này
            connection_attempts=5,
            retry_delay=5,
            heartbeat=600
        )
        
        # 3. Mở kết nối
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        
        # 4. Khai báo queue
        channel.queue_declare(queue='analytics_queue', durable=True)
        
        # 5. Chuẩn bị nội dung
        message = {"event": event_type}
        if data:
            message.update(data)
            
        # 6. Publish tin nhắn
        channel.basic_publish(
            exchange='',
            routing_key='analytics_queue',
            body=json.dumps(message),
            properties=pika.BasicProperties(
                delivery_mode=2,  # Tin nhắn không mất khi RabbitMQ restart
                content_type='application/json'
            )
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
                "role": u.role,
                "status": u.status,
                "package_name": getattr(u, 'package_name', 'Free'), 
                "user_level": getattr(u, 'user_level', 'A1 (Beginner)')
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 2. HÀM LẤY PHẢN HỒI ---
@user_bp.route("/feedbacks/all", methods=["GET"])
def get_all_feedbacks():
    try:
        results = db.session.query(Feedback, User).join(User, Feedback.user_id == User.id).all()
        output = []
        for fb, u in results:
            output.append({
                "email": u.email,
                "target": fb.target_name,
                "content": fb.content,
                "rating": fb.rating,
                "date": fb.created_at.strftime("%d/%m/%Y")
            })
        return jsonify(output), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 3. HÀM ĐĂNG KÝ ---
@user_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json(force=True, silent=True) or {}
    
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    role = (data.get("role") or "learner").strip().lower()

    if not email or not password:
        return jsonify({"error": "Missing email or password"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email already exists"}), 409

    try:
        # Tạo user mới
        u = User(email=email, password=generate_password_hash(password), role=role)
        db.session.add(u)
        db.session.commit()

        # BẮN TIN NHẮN SANG ANALYTICS SERVICE
        send_to_analytics("new_user", {"email": email, "id": str(u.id)})

        return jsonify({"id": u.id, "message": "User created"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500