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
        params.socket_timeout = 5  
        
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
        print(f">>> [MQ Warning]: Không thể gửi message: {e}")

# --- 1. ĐĂNG KÝ ---
@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    user_role = (data.get("role") or "learner").lower()
    
    if not email or not password:
        return jsonify({"message": "Email và mật khẩu là bắt buộc"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email này đã được đăng ký!"}), 409

    try:
        initial_status = "pending" if user_role == "mentor" else "active"

        new_user = User(
            id=str(uuid.uuid4()),
            username=data.get("username") or email.split('@')[0],
            email=email,
            password=generate_password_hash(password),
            role=user_role,
            status=initial_status
        )
        db.session.add(new_user)
        db.session.commit()

        send_mq_message({
            "event": "USER_REGISTERED",
            "user_id": new_user.id,
            "username": new_user.username,
            "email": new_user.email,
            "role": new_user.role,
            "status": initial_status
        })

        return jsonify({
            "message": "Đăng ký thành công", 
            "status": initial_status,
            "user_id": new_user.id
        }), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi lưu Database: {str(e)}"}), 500

# --- 2. ĐĂNG NHẬP QUA FIREBASE ---
@auth_bp.route("/login-firebase", methods=["POST"])
def login_firebase():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    user_role = (data.get("role") or "learner").lower()
    
    if not email:
        return jsonify({"error": "Thiếu email từ Firebase"}), 400

    try:
        user = User.query.filter_by(email=email).first()
        is_new = False

        if not user:
            is_new = True
            initial_status = "pending" if user_role == "mentor" else "active"
            user = User(
                id=str(uuid.uuid4()),
                username=data.get("username") or email.split('@')[0],
                email=email,
                password="FIREBASE_AUTHENTICATED",
                role=user_role,
                status=initial_status
            )
            db.session.add(user)
            db.session.commit()
        
        if user.status != "active":
            return jsonify({
                "error": "Tài khoản của bạn đang bị khóa hoặc chờ duyệt",
                "status": user.status
            }), 403

        additional_claims = {
            "user_id": str(user.id),
            "role": user.role,
            "status": user.status
        }
        token = create_access_token(identity=str(user.id), additional_claims=additional_claims)

        if is_new:
            send_mq_message({
                "event": "USER_REGISTERED",
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "role": user.role,
                "status": user.status
            })

        return jsonify({
            "token": token,
            "user": {
                "id": user.id, 
                "email": user.email, 
                "role": user.role, 
                "status": user.status,
                "username": user.username,
                "level": user.user_level,
                "package_id": user.package_id,      # MỚI CẬP NHẬT
                "package_name": user.package_name   # MỚI CẬP NHẬT
            }
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Lỗi đồng bộ Firebase: {str(e)}"}), 500

# --- 3. ĐĂNG NHẬP THƯỜNG ---
@auth_bp.route("/login", methods=["POST"])
def login():
    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    
    try:
        user = User.query.filter_by(email=email).first()
        if not user or not check_password_hash(user.password, password):
            return jsonify({"error": "Email hoặc mật khẩu không chính xác"}), 401
        
        if user.status != "active":
            return jsonify({
                "error": "Tài khoản đã bị khóa hoặc đang chờ quản trị viên phê duyệt.",
                "status": user.status
            }), 403
            
        additional_claims = {
            "user_id": str(user.id), 
            "role": user.role,
            "status": user.status
        }
        token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
        
        return jsonify({
            "token": token, 
            "user": {
                "id": user.id, 
                "email": user.email, 
                "role": user.role, 
                "status": user.status,
                "username": user.username,
                "level": user.user_level,
                "package_id": user.package_id,      # MỚI CẬP NHẬT
                "package_name": user.package_name   # MỚI CẬP NHẬT
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 4. CẬP NHẬT ROLE & TRẠNG THÁI ---
@auth_bp.route("/update-role", methods=["POST"])
def update_role():
    data = request.get_json() or {}
    user_id = data.get('id')
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User không tồn tại"}), 404
            
        old_role = user.role.lower() if user.role else ""
        new_role = (data.get('role') or old_role).lower()
        
        user.username = data.get('username', user.username)
        user.role = new_role
        
        if data.get('status'):
            user.status = data.get('status').lower()
        elif old_role != 'mentor' and new_role == 'mentor':
            user.status = 'pending'
        
        if data.get('password'):
            user.password = generate_password_hash(data.get('password'))
        
        db.session.commit()

        send_mq_message({
            "event": "USER_UPDATED",
            "user_id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role,
            "status": user.status
        })

        return jsonify({"message": "Cập nhật thành công", "status": user.status}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi cập nhật: {str(e)}"}), 500

# --- 5. API DUYỆT NGƯỜI DÙNG (ADMIN) ---
@auth_bp.route("/verify-user/<string:user_id>", methods=["POST"])
def verify_user(user_id):
    try:
        data = request.get_json()
        action = data.get('action') 
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "Không tìm thấy người dùng"}), 404
        
        new_status = 'active' if action == 'approve' else 'rejected'
        user.status = new_status
        db.session.commit()

        send_mq_message({
            "event": "USER_STATUS_UPDATED",
            "user_id": user.id,
            "status": new_status
        })

        return jsonify({"message": f"Đã cập nhật trạng thái thành {new_status}"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# --- 6. API CẬP NHẬT STATUS NHANH ---
@auth_bp.route("/update-status", methods=["POST"])
def update_status():
    data = request.get_json() or {}
    user_id = data.get('id')
    new_status = data.get('status') 

    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User không tồn tại"}), 404
        
        user.status = new_status
        db.session.commit()

        return jsonify({"message": "Cập nhật trạng thái thành công"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
# cập nhật level
@auth_bp.route("/update-level", methods=["POST"]) # Đặt tên mới cho đúng chức năng
def update_level():
    data = request.get_json() or {}
    user_id = data.get('id')
    try:
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User không tồn tại"}), 404
            
        # Chỉ tập trung cập nhật trình độ
        if data.get('user_level'):
            user.user_level = data.get('user_level')
            db.session.commit()
            
            # Gửi tin nhắn đến RabbitMQ để Mentor Service biết học viên đã có trình độ mới
            send_mq_message({
                "event": "USER_LEVEL_UPDATED",
                "user_id": user.id,
                "level": user.user_level
            })
            
            return jsonify({"message": "Cập nhật trình độ thành công", "level": user.user_level}), 200
        
        return jsonify({"message": "Thiếu dữ liệu user_level"}), 400
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500