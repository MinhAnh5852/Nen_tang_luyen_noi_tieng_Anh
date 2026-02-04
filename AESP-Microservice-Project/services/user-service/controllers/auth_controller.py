# import os
# import pika
# import json
# import uuid
# from flask import Blueprint, request, jsonify
# from werkzeug.security import generate_password_hash, check_password_hash
# from database import db
# from models.user import User
# from flask_jwt_extended import create_access_token

# auth_bp = Blueprint("auth", __name__)

# # --- HÀM BỔ TRỢ: GỬI TIN NHẮN ĐẾN RABBITMQ ---
# def send_mq_message(message):
#     try:
#         # Ưu tiên lấy URL từ biến môi trường RABBITMQ_URL
#         url = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@app-rabbitmq:5672/')
#         params = pika.URLParameters(url)
#         params.socket_timeout = 5  # Thêm timeout để tránh treo app
        
#         connection = pika.BlockingConnection(params)
#         channel = connection.channel()
        
#         channel.queue_declare(queue='user_events', durable=True)
        
#         channel.basic_publish(
#             exchange='',
#             routing_key='user_events',
#             body=json.dumps(message),
#             properties=pika.BasicProperties(delivery_mode=2)
#         )
#         connection.close()
#         print(f">>> [MQ Success]: Đã gửi sự kiện {message.get('event')}")
#     except Exception as e:
#         # CHỈ IN LỖI, KHÔNG QUĂNG EXCEPTION ĐỂ TRÁNH ROLLBACK DB
#         print(f">>> [MQ Warning]: Không thể gửi message: {e}")

# # --- 1. ĐĂNG KÝ ---
# @auth_bp.route("/register", methods=["POST"])
# def register():
#     data = request.get_json() or {}
#     email = (data.get("email") or "").strip().lower()
#     password = data.get("password")
    
#     if not email or not password:
#         return jsonify({"message": "Email và mật khẩu là bắt buộc"}), 400

#     if User.query.filter_by(email=email).first():
#         return jsonify({"message": "Email này đã được đăng ký!"}), 409

#     try:
#         new_user = User(
#             id=str(uuid.uuid4()),
#             username=data.get("username") or email.split('@')[0],
#             email=email,
#             password=generate_password_hash(password),
#             role=(data.get("role") or "learner").lower(),
#             status="active"
#         )
#         db.session.add(new_user)
#         db.session.commit()

#         # Đồng bộ an toàn
#         send_mq_message({
#             "event": "USER_REGISTERED",
#             "user_id": new_user.id,
#             "username": new_user.username,
#             "email": new_user.email,
#             "role": new_user.role
#         })

#         return jsonify({"message": "Đăng ký thành công", "user_id": new_user.id}), 201
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"message": f"Lỗi lưu Database: {str(e)}"}), 500

# # --- 2. ĐĂNG NHẬP QUA FIREBASE ---
# @auth_bp.route("/login-firebase", methods=["POST"])
# def login_firebase():
#     data = request.get_json() or {}
#     email = (data.get("email") or "").strip().lower()
    
#     if not email:
#         return jsonify({"error": "Thiếu email từ Firebase"}), 400

#     try:
#         user = User.query.filter_by(email=email).first()
#         is_new = False

#         if not user:
#             is_new = True
#             user = User(
#                 id=str(uuid.uuid4()),
#                 username=data.get("username") or email.split('@')[0],
#                 email=email,
#                 password="FIREBASE_AUTHENTICATED",
#                 role="learner",
#                 status="active"
#             )
#             db.session.add(user)
#             db.session.commit()

#         # QUAN TRỌNG: Thêm user_id và role vào payload của Token
#         additional_claims = {
#             "user_id": str(user.id),
#             "role": user.role
#         }
#         token = create_access_token(identity=str(user.id), additional_claims=additional_claims)

#         if is_new:
#             send_mq_message({
#                 "event": "USER_REGISTERED",
#                 "user_id": user.id,
#                 "username": user.username,
#                 "email": user.email,
#                 "role": user.role
#             })

#         return jsonify({
#             "token": token,
#             "user": {
#                 "id": user.id, 
#                 "email": user.email, 
#                 "role": user.role, 
#                 "username": user.username
#             }
#         }), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"error": f"Lỗi đồng bộ Firebase: {str(e)}"}), 500

# # --- 3. ĐĂNG NHẬP THƯỜNG ---
# @auth_bp.route("/login", methods=["POST"])
# def login():
#     data = request.get_json(silent=True) or {}
#     email = (data.get("email") or "").strip().lower()
#     password = data.get("password")
    
#     try:
#         user = User.query.filter_by(email=email).first()
#         if not user or not check_password_hash(user.password, password):
#             return jsonify({"error": "Email hoặc mật khẩu không chính xác"}), 401
            
#         # Thêm thông tin vào token tương tự Firebase login
#         additional_claims = {"user_id": str(user.id), "role": user.role}
#         token = create_access_token(identity=str(user.id), additional_claims=additional_claims)
        
#         return jsonify({
#             "token": token, 
#             "user": {
#                 "id": user.id, 
#                 "email": user.email, 
#                 "role": user.role, 
#                 "username": user.username
#             }
#         }), 200
#     except Exception as e:
#         return jsonify({"error": str(e)}), 500

# # --- 4. CẬP NHẬT ROLE ---
# @auth_bp.route("/update-role", methods=["POST"])
# def update_role():
#     data = request.get_json() or {}
#     user_id = data.get('id')
#     try:
#         user = User.query.get(user_id)
#         if not user:
#             return jsonify({"message": "User không tồn tại"}), 404
            
#         old_role = user.role
#         new_role = (data.get('role') or old_role).lower()
        
#         user.username = data.get('username', user.username)
#         user.role = new_role
        
#         if data.get('password'):
#             user.password = generate_password_hash(data.get('password'))
        
#         db.session.commit()

#         if old_role != 'mentor' and new_role == 'mentor':
#             send_mq_message({
#                 "event": "USER_REGISTERED",
#                 "user_id": user.id,
#                 "username": user.username,
#                 "email": user.email,
#                 "role": "mentor"
#             })

#         return jsonify({"message": "Cập nhật thành công"}), 200
#     except Exception as e:
#         db.session.rollback()
#         return jsonify({"message": f"Lỗi cập nhật: {str(e)}"}), 500
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
        # LOGIC: Mentor đăng ký mới phải ở trạng thái pending
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

        # Bắn MQ kèm Status để Mentor Service hiện badge cam nhấp nháy
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
                "username": user.username
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
                "username": user.username
            }
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 4. CẬP NHẬT ROLE (GIỮ LẠI LOGIC CŨ) ---
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
        
        # Nếu nâng cấp lên mentor thì để trạng thái chờ duyệt
        if old_role != 'mentor' and new_role == 'mentor':
            user.status = 'pending'
        
        if data.get('password'):
            user.password = generate_password_hash(data.get('password'))
        
        db.session.commit()

        if old_role != 'mentor' and new_role == 'mentor':
            send_mq_message({
                "event": "USER_REGISTERED",
                "user_id": user.id,
                "username": user.username,
                "email": user.email,
                "role": "mentor",
                "status": "pending"
            })

        return jsonify({"message": "Cập nhật thành công", "status": user.status}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": f"Lỗi cập nhật: {str(e)}"}), 500

# --- 5. API DUYỆT NGƯỜI DÙNG (MỚI - ĐỂ ADMIN DUYỆT TRÊN BẢNG USERS) ---
@auth_bp.route("/verify-user/<string:user_id>", methods=["POST"])
def verify_user(user_id):
    try:
        data = request.get_json()
        action = data.get('action') # approve hoặc reject
        
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "Không tìm thấy người dùng"}), 404
        
        new_status = 'active' if action == 'approve' else 'rejected'
        user.status = new_status
        db.session.commit()

        # Bắn MQ để các service khác cập nhật theo
        send_mq_message({
            "event": "USER_STATUS_UPDATED",
            "user_id": user.id,
            "status": new_status
        })

        return jsonify({"message": f"Đã cập nhật trạng thái thành {new_status}"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500