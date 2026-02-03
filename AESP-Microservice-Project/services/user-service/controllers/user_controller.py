import os
import pika
import json
import uuid
from datetime import date
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
        rabbitmq_url = os.environ.get('RABBITMQ_URL', 'amqp://admin:admin123@app-rabbitmq:5672/')
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
    except Exception as e:
        print(f"!!! RabbitMQ Warning: {e}") 
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
        user_id = get_jwt_identity()
        user = User.query.get(user_id)
        if not user:
            return jsonify({"message": "User không tồn tại"}), 404
        
        return jsonify({
            "id": user.id,
            "username": user.username or user.email.split('@')[0],
            "email": user.email,
            "role": str(user.role).lower(),
            "package_name": user.package_name or 'Free',
            "user_level": user.user_level,
            "points": user.total_learning_points,
            "streak": user.current_streak
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 3. CẬP NHẬT TRÌNH ĐỘ (Sau bài Assessment) ---
@user_bp.route("/profile/update-level", methods=["POST"])
@jwt_required()
def update_user_level():
    try:
        data = request.get_json()
        user_id = get_jwt_identity()
        new_level = data.get('user_level')
        
        user = User.query.get(user_id)
        if not user: return jsonify({"error": "User không tồn tại"}), 404
        
        user.user_level = new_level
        db.session.commit()

        send_to_mq("USER_LEVEL_UPDATED", {"user_id": user_id, "new_level": new_level})
        return jsonify({"message": f"Đã cập nhật trình độ thành {new_level}"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# --- 4. CẬP NHẬT TIẾN ĐỘ (Khi luyện tập tại Practice.tsx) ---
@user_bp.route("/profile/update-progress", methods=["POST"])
@jwt_required()
def update_user_progress():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        accuracy = data.get('accuracy', 0)
        
        user = User.query.get(user_id)
        if not user: return jsonify({"error": "User không tồn tại"}), 404

        # Cộng điểm: 1% accuracy = 1 point
        user.total_learning_points += int(accuracy)
        
        # Cập nhật Streak
        today = date.today()
        if user.last_practice_date:
            delta = (today - user.last_practice_date).days
            if delta == 1: user.current_streak += 1
            elif delta > 1: user.current_streak = 1
        else:
            user.current_streak = 1
            
        user.last_practice_date = today
        db.session.commit()

        send_to_mq("USER_PROGRESS_UPDATED", {
            "user_id": user_id, 
            "points_added": int(accuracy),
            "streak": user.current_streak
        })
        return jsonify({"message": "Ghi nhận tiến độ thành công"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# --- 5. BẢNG XẾP HẠNG (Leaderboard) ---
@user_bp.route("/leaderboard", methods=["GET"])
def get_leaderboard():
    try:
        top_users = User.query.filter_by(role='learner') \
            .order_by(User.total_learning_points.desc()) \
            .limit(10).all()
        
        result = []
        for index, u in enumerate(top_users):
            result.append({
                "rank": index + 1,
                "username": u.username or u.email.split('@')[0],
                "points": u.total_learning_points,
                "level": u.user_level,
                "streak": u.current_streak
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- 6. ĐĂNG KÝ ---
@user_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    
    if User.query.filter_by(email=email).first():
        return jsonify({"error": "Email đã tồn tại"}), 409

    try:
        u = User(
            id=str(uuid.uuid4()), 
            email=email, 
            username=data.get("username") or email.split('@')[0],
            password=generate_password_hash(password), 
            role=(data.get("role") or "learner").lower()
        )
        db.session.add(u)
        db.session.commit()
        
        send_to_mq("USER_REGISTERED", {"user_id": u.id, "email": u.email})
        return jsonify({"id": u.id, "message": "Thành công"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
    
    # --- 7. CẬP NHẬT THÔNG TIN CÁ NHÂN (Dành cho trang Profile) ---
@user_bp.route("/profile/update", methods=["PUT"])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User không tồn tại"}), 404
        
        # Cập nhật username nếu có trong request
        if 'username' in data:
            user.username = data.get('username')
            
        db.session.commit()
        return jsonify({"message": "Cập nhật hồ sơ thành công"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500