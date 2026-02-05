import os
import pika
import json
import uuid
from datetime import date
from flask import Blueprint, request, jsonify
from flask_jwt_extended import jwt_required, get_jwt_identity
from sqlalchemy import func
from werkzeug.security import generate_password_hash
from database import db
from models.user import User, Feedback, MentorSelection

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
            "package_id": user.package_id,
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

        user.total_learning_points += int(accuracy)
        
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
    
# --- 7. CẬP NHẬT THÔNG TIN CÁ NHÂN ---
@user_bp.route("/profile/update", methods=["PUT"])
@jwt_required()
def update_profile():
    try:
        user_id = get_jwt_identity()
        data = request.get_json()
        user = User.query.get(user_id)
        if not user:
            return jsonify({"error": "User không tồn tại"}), 404
        
        if 'username' in data:
            user.username = data.get('username')
            
        db.session.commit()
        return jsonify({"message": "Cập nhật hồ sơ thành công"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# --- 8. NÂNG CẤP GÓI NỘI BỘ ---
@user_bp.route("/internal/upgrade-package", methods=["POST"])
def internal_upgrade():
    try:
        data = request.json
        user_id = data.get('user_id')
        package_name = data.get('package_name')
        package_id = data.get('package_id')
        
        user = User.query.get(user_id)
        if user:
            user.package_name = package_name
            user.package_id = package_id
            db.session.commit()
            
            send_to_mq("USER_PACKAGE_UPGRADED", {
                "user_id": user_id, 
                "package_name": package_name,
                "package_id": package_id
            })
            return jsonify({"status": "success"}), 200
        return jsonify({"error": "User không tồn tại"}), 404
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500

# --- 9. QUẢN LÝ MENTOR SELECTIONS ---

@user_bp.route("/mentors/available", methods=["GET"])
def get_available_mentors():
    try:
        mentors = User.query.filter_by(role='mentor', status='active').all()
        return jsonify([{
            "id": m.id,
            "username": m.username,
            "skills": m.package_name if m.package_name else "English Expert",
            "rating": 5.0
        } for m in mentors]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@user_bp.route("/my-mentor/<string:user_id>", methods=["GET"])
def get_my_mentor(user_id):
    try:
        selection = MentorSelection.query.filter_by(learner_id=user_id, status='active').first()
        if selection:
            mentor = User.query.get(selection.mentor_id)
            if mentor:
                return jsonify({
                    "id": mentor.id,
                    "username": mentor.username,
                    "skills": mentor.package_name
                }), 200
        return jsonify(None), 200 
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# user-service/controllers/user_controller.py

@user_bp.route("/mentors/select", methods=["POST"])
def select_mentor():
    data = request.get_json() or {}
    # Ép kiểu string để tránh lỗi dữ liệu object từ Frontend gửi lên
    learner_id = str(data.get('learner_id'))
    mentor_id = str(data.get('mentor_id'))

    # Kiểm tra dữ liệu đầu vào để tránh crash DB
    if not data.get('learner_id') or not data.get('mentor_id'):
        return jsonify({"error": "Thiếu thông tin người học hoặc cố vấn"}), 400

    try:
        # 1. Kiểm tra xem người học đã kết nối với chính Mentor này chưa
        existing = MentorSelection.query.filter_by(
            learner_id=learner_id, 
            mentor_id=mentor_id, 
            status='active'
        ).first()
        
        if existing:
            return jsonify({"message": "Bạn đang trong lộ trình học tập với cố vấn này"}), 200

        # 2. Hủy (deactivate) toàn bộ kết nối cũ để đảm bảo mỗi lúc chỉ có 1 Mentor hướng dẫn
        MentorSelection.query.filter_by(
            learner_id=learner_id, 
            status='active'
        ).update({"status": "inactive"})

        # 3. Tạo bản ghi kết nối mới
        new_selection = MentorSelection(
            learner_id=learner_id,
            mentor_id=mentor_id,
            status='active'
        )
        db.session.add(new_selection)
        
        # Lưu thay đổi xuống Database
        db.session.commit()

        # 4. Gửi thông báo qua RabbitMQ để các service khác (như Mentor Service) cập nhật lộ trình
        send_to_mq("MENTOR_SELECTED", {
            "learner_id": learner_id, 
            "mentor_id": mentor_id
        })
        
        return jsonify({"message": "Kết nối với Cố vấn thành công!"}), 201

    except Exception as e:
        # Rollback để tránh treo Database session khi gặp lỗi
        db.session.rollback()
        # In lỗi chi tiết ra Log Docker để bạn dễ theo dõi
        print(f"--- [CRITICAL ERROR SELECT MENTOR]: {str(e)} ---")
        return jsonify({"error": "Lỗi hệ thống khi thiết lập cố vấn"}), 500
# user-service/controllers/user_controller.py

@user_bp.route("/mentors/my-learners/<string:mentor_id>", methods=["GET"])
def get_my_learners(mentor_id):
    try:
        # 1. Tìm tất cả các kết nối đang 'active' của Mentor này trong bảng mentor_selections
        # Đảm bảo bạn đã import MentorSelection ở đầu file
        selections = MentorSelection.query.filter_by(mentor_id=mentor_id, status='active').all()
        
        # 2. Lấy thông tin chi tiết của từng học viên từ bảng User
        learner_list = []
        for s in selections:
            learner = User.query.get(s.learner_id)
            if learner:
                learner_list.append({
                    "id": learner.id,
                    "username": learner.username or learner.email.split('@')[0],
                    "email": learner.email,
                    "user_level": learner.user_level or 'A1',
                    "status": learner.status or 'active'
                })
        
        # 3. Trả về danh sách (nếu trống sẽ trả về [])
        return jsonify(learner_list), 200
    except Exception as e:
        print(f"Lỗi GET_MY_LEARNERS: {str(e)}")
        return jsonify({"error": str(e)}), 500
@user_bp.route("/mentors/tasks", methods=["POST"])
@jwt_required()
def create_task_v2():
    data = request.get_json()
    mentor_id = get_jwt_identity()
    
    # Ép kiểu dữ liệu để an toàn
    learner_id = str(data.get('learner_id'))
    
    try:
        from sqlalchemy import text
        # Bạn dùng câu lệnh SQL thuần để insert cho nhanh và khớp với bảng tasks bạn đã tạo
        sql = text("""
            INSERT INTO tasks (mentor_id, learner_id, learner_name, title, description, deadline, status) 
            VALUES (:mid, :lid, :lname, :tit, :desc, :dead, 'Pending')
        """)
        
        db.session.execute(sql, {
            "mid": mentor_id,
            "lid": learner_id,
            "lname": data.get('learner_name', 'Học viên'),
            "tit": data.get('title'),
            "desc": data.get('description'),
            "dead": data.get('deadline')
        })
        db.session.commit()
        return jsonify({"message": "Giao bài thành công"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
# --- ROUTE BỔ SUNG: LẤY DANH SÁCH BÀI TẬP ĐÃ GIAO ---
@user_bp.route("/mentors/tasks", methods=["GET"])
@jwt_required()
def get_mentor_tasks():
    try:
        from sqlalchemy import text
        mentor_id = get_jwt_identity()
        
        # Lấy danh sách bài tập mà Mentor này đã giao, sắp xếp theo ngày tạo mới nhất
        sql = text("""
            SELECT id, title, learner_name, status, deadline 
            FROM tasks 
            WHERE mentor_id = :mid 
            ORDER BY created_at DESC
        """)
        
        result = db.session.execute(sql, {"mid": mentor_id}).mappings().all()
        
        # Chuyển đổi dữ liệu sang dạng danh sách JSON
        tasks = []
        for row in result:
            tasks.append({
                "id": row['id'],
                "title": row['title'],
                "learner_name": row['learner_name'],
                "status": row['status'],
                "deadline": str(row['deadline']) if row['deadline'] else "Không hạn"
            })
            
        return jsonify(tasks), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --- ROUTE BỔ SUNG: XÓA BÀI TẬP ---
@user_bp.route("/mentors/tasks/<int:task_id>", methods=["DELETE"])
@jwt_required()
def delete_mentor_task(task_id):
    try:
        from sqlalchemy import text
        mentor_id = get_jwt_identity()
        
        # Chỉ cho phép Mentor xóa bài tập do chính họ giao
        sql = text("DELETE FROM tasks WHERE id = :tid AND mentor_id = :mid")
        db.session.execute(sql, {"tid": task_id, "mid": mentor_id})
        db.session.commit()
        
        return jsonify({"message": "Xóa bài tập thành công"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500
# user-service/controllers/user_controller.py

@user_bp.route("/mentors/submissions/grade", methods=["POST"])
@jwt_required()
def grade_submission():
    data = request.get_json()
    try:
        from sqlalchemy import text
        # Lưu vào bảng submissions để Learner xem được phản hồi của Mentor
        sql = text("""
            INSERT INTO submissions (learner_id, task_title, audio_link, score, feedback, status)
            VALUES (:lid, :title, :link, :score, :fb, 'Graded')
            ON DUPLICATE KEY UPDATE score = :score, feedback = :fb, status = 'Graded'
        """)
        
        db.session.execute(sql, {
            "lid": data.get('learner_id'),
            "title": data.get('topic'),
            "link": data.get('audio_url'),
            "score": data.get('score'),
            "fb": data.get('comment')
        })
        db.session.commit()
        return jsonify({"message": "Đã lưu điểm và nhận xét!"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500