from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import create_engine, text
import json
from datetime import datetime
import os
from werkzeug.utils import secure_filename


mentor_bp = Blueprint('mentor', __name__)

# --- HÀM HỖ TRỢ: KẾT NỐI DATABASE ---
def get_db_connection():
    db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    if 'mentor_management_db' in db_url:
        db_url = db_url.replace('mentor_management_db', 'user_db')
    if not db_url:
        db_url = 'mysql+pymysql://root:root@user-db:3306/user_db?charset=utf8mb4'
    return create_engine(db_url)

# ==================================================
# 1. API Đăng ký Mentor (Profile chi tiết)
# ==================================================
@mentor_bp.route('/', methods=['POST'])
def create_mentor():
    try:
        data = request.json
        uid = data.get('user_id')
        if not uid: return jsonify({'error': 'Thieu user_id'}), 400

        skills_val = ",".join(data.get('skills', [])) if isinstance(data.get('skills'), list) else data.get('skills', '')
        
        engine = get_db_connection()
        with engine.connect() as conn:
            check = conn.execute(text("SELECT id FROM mentors WHERE user_id = :uid"), {"uid": uid}).fetchone()
            if check: return jsonify({'error': 'User nay da la Mentor'}), 409
            
            query = text("""
                INSERT INTO mentors (user_id, username, email, full_name, bio, skills, status) 
                VALUES (:uid, :uname, :email, :fname, :bio, :skills, 'pending')
            """)
            conn.execute(query, {
                "uid": uid,
                "uname": data.get('username', ''),
                "email": data.get('email', ''),
                "fname": data.get('full_name', ''),
                "bio": data.get('bio', ''),
                "skills": skills_val
            })
            conn.commit()
        return jsonify({'message': 'Dang ky thanh cong'}), 201
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 2. API Lấy danh sách (QUÉT CẢ BẢNG USERS ĐỂ HIỆN PENDING)
# ==================================================
@mentor_bp.route('/profiles', methods=['GET'])
def get_mentors():
    try:
        engine = get_db_connection()
        mentors = []
        with engine.connect() as conn:
            # JOIN users và mentors để lấy cả những ông mới đăng ký (chỉ có bên users)
            result = conn.execute(text("""
                SELECT u.id as user_id, u.username, u.email, u.status, m.skills 
                FROM users u
                LEFT JOIN mentors m ON u.id = m.user_id
                WHERE u.role = 'mentor'
                ORDER BY CASE WHEN u.status = 'pending' THEN 0 ELSE 1 END, u.created_at DESC
            """))
            
            for row in result:
                skills_list = []
                if row.skills:
                    skills_list = [s.strip() for s in str(row.skills).split(',')]
                else:
                    skills_list = ["Chờ cập nhật"]

                mentors.append({
                    'id': row.user_id, 
                    'username': row.username or "Unknown",
                    'email': row.email or "N/A",
                    'skills': skills_list,
                    'status': (row.status or 'pending').lower()
                })
        return jsonify(mentors), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 3. API Duyệt Mentor (Cập nhật cả 2 bảng)
# ==================================================
@mentor_bp.route('/verify/<string:user_id>', methods=['POST'])
def verify_mentor(user_id):
    try:
        data = request.json
        action = data.get('action')
        new_status = 'active' if action == 'approve' else 'rejected'
        
        engine = get_db_connection()
        with engine.connect() as conn:
            # 1. Cập nhật bảng users (Quan trọng để Login)
            conn.execute(text("UPDATE users SET status = :st WHERE id = :uid"), 
                         {"st": new_status, "uid": user_id})
            
            # 2. Cập nhật hoặc tạo profile bên bảng mentors
            if action == 'approve':
                conn.execute(text("""
                    INSERT INTO mentors (user_id, status, skills) 
                    VALUES (:uid, 'active', 'Chưa cập nhật')
                    ON DUPLICATE KEY UPDATE status = 'active'
                """), {"uid": user_id})
            conn.commit()
        return jsonify({'message': f'Da cap nhat thanh cong sang {new_status}'}), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 4. API Xóa Mentor
# ==================================================
@mentor_bp.route('/<string:user_id>', methods=['DELETE'])
def delete_mentor(user_id):
    try:
        engine = get_db_connection()
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM mentors WHERE user_id = :uid"), {"uid": user_id})
            conn.commit()
        return jsonify({'message': 'Da xoa mentor'}), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 5. API Lấy danh sách Học viên
# ==================================================
# Trong mentor_controller.py
@mentor_bp.route('/learners-list', methods=['GET'])
def get_learners_list():
    try:
        # 1. Lấy mentor_id từ thông tin đăng nhập (Bảo có thể dùng JWT ở đây)
        # Nếu chưa dùng JWT, ta có thể tạm lấy từ query string để test
        mentor_id = request.args.get('mentor_id') 

        engine = get_db_connection()
        learners = []
        with engine.connect() as conn:
            # 2. Sửa câu Query: Chỉ lấy học viên thuộc task/session của Mentor này
            # Ví dụ: Lấy những học viên mà Mentor này đã từng giao bài tập (tasks)
            query = text("""
                SELECT DISTINCT u.id, u.username, u.email, u.user_level, u.status
                FROM users u
                JOIN tasks t ON u.id = t.learner_id
                WHERE t.mentor_id = :mid AND u.role = 'learner'
            """)
            
            # Nếu Bảo muốn lấy danh sách Mentor đã được "duyệt" quản lý học viên:
            # query = text("SELECT * FROM users WHERE role = 'learner' AND assigned_mentor = :mid")

            result = conn.execute(query, {"mid": mentor_id})
            for row in result: 
                learners.append({
                    'id': row.id, 
                    'username': row.username or 'Học viên', 
                    'email': row.email, 
                    'level': row.user_level, 
                    'status': row.status
                })
        return jsonify(learners), 200
    except Exception as e: 
        return jsonify({'error': str(e)}), 500

# ==================================================
# 6. API Gửi tin nhắn
# ==================================================
@mentor_bp.route('/messages', methods=['POST'])
def send_message():
    try:
        data = request.json
        engine = get_db_connection()
        with engine.connect() as conn:
            query = text("INSERT INTO messages (sender_id, receiver_id, receiver_name, content) VALUES (:sid, :rid, :rname, :cont)")
            conn.execute(query, {
                "sid": data.get('sender_id', 'Unknown'),
                "rid": data['receiver_id'],
                "rname": data.get('receiver_name', ''),
                "cont": data['content']
            })
            conn.commit()
        return jsonify({'message': 'Gui tin nhan thanh cong!'}), 201
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 7. API Lấy Tiến Độ
# ==================================================
@mentor_bp.route('/learner-progress/<string:learner_id>', methods=['GET'])
def get_learner_progress(learner_id):
    try:
        engine = get_db_connection()
        with engine.connect() as conn:
            sessions = conn.execute(text("SELECT * FROM learning_sessions WHERE learner_id = :lid AND score > 0 ORDER BY created_at DESC"), {"lid": learner_id}).fetchall()
            total_tasks = conn.execute(text("SELECT COUNT(*) FROM tasks WHERE learner_id = :lid"), {"lid": learner_id}).scalar() or 10
            
            if not sessions:
                return jsonify({"completed_lessons": 0, "total_lessons": total_tasks, "average_score": 0, "recent_history": []}), 200

            total_score = sum(s.score for s in sessions)
            avg = round(total_score / len(sessions), 1)
            history = [{"date": s.created_at.strftime('%d/%m/%Y'), "lesson": s.lesson_name, "score": s.score} for s in sessions[:5]]
            
            return jsonify({
                "completed_lessons": len(sessions), "total_lessons": total_tasks, "average_score": avg, "recent_history": history
            }), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 8. API Lấy Phản hồi
# ==================================================
@mentor_bp.route('/learner-feedback/<string:learner_id>', methods=['GET'])
def get_learner_feedback(learner_id):
    try:
        engine = get_db_connection()
        feedbacks = []
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM feedbacks WHERE user_id = :lid ORDER BY created_at DESC"), {"lid": learner_id}).fetchall()
            for row in result: 
                feedbacks.append({
                    'comment': row.ai_comment, 'sentiment': row.sentiment, 'date': row.created_at.strftime('%d/%m/%Y %H:%M')
                })
        return jsonify(feedbacks), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 9. API Tạo bài tập
# ==================================================
@mentor_bp.route('/tasks', methods=['POST'])
def create_task():
    try:
        data = request.json
        engine = get_db_connection()
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO tasks (learner_id, learner_name, title, description, deadline, status) VALUES (:lid, :lname, :tit, :desc, :dead, 'Pending')"), 
                         {"lid": data['learner_id'], "lname": data['learner_name'], "tit": data['title'], "desc": data['description'], "dead": data['deadline']})
            conn.commit()
        return jsonify({'message': 'Giao bài thành công'}), 201
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 10. API Lấy bài tập
# ==================================================
@mentor_bp.route('/tasks', methods=['GET'])
def get_tasks():
    try:
        engine = get_db_connection()
        tasks = []
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM tasks ORDER BY created_at DESC"))
            for row in result: tasks.append({'id': row.id, 'learner_name': row.learner_name, 'title': row.title, 'deadline': str(row.deadline), 'status': row.status})
        return jsonify(tasks), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 11. API Xếp Hạng
# ==================================================
@mentor_bp.route('/rankings', methods=['GET'])
def get_rankings():
    try:
        engine = get_db_connection()
        ranking_data = []
        with engine.connect() as conn:
            query = text("""
                SELECT u.username as name, ROUND(AVG(ls.score), 2) as avg_score 
                FROM users u
                JOIN learning_sessions ls ON u.id = ls.learner_id
                GROUP BY u.id ORDER BY avg_score DESC
            """)
            result = conn.execute(query).fetchall()
            for r in result:
                ranking_data.append({'name': r.name, 'avg_score': r.avg_score})
        return jsonify(ranking_data), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 12. API Tạo Tài Liệu
# ==================================================
@mentor_bp.route('/resources', methods=['POST'])
def create_resource():
    try:
        data = request.json
        engine = get_db_connection()
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO resources (title, link, skill_type, description) VALUES (:tit, :lnk, :sk, :desc)"), 
                         {"tit": data['title'], "lnk": data['link'], "sk": data['skill_type'], "desc": data['description']})
            conn.commit()
        return jsonify({'message': 'Them tai lieu thanh cong'}), 201
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 13. API Lấy Tài Liệu
# ==================================================
@mentor_bp.route('/resources', methods=['GET'])
def get_resources():
    try:
        engine = get_db_connection()
        resources = []
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM resources ORDER BY created_at DESC"))
            for row in result: resources.append({'id': row.id, 'title': row.title, 'link': row.link, 'skill_type': row.skill_type, 'date': row.created_at.strftime('%d/%m/%Y')})
        return jsonify(resources), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 22. API Lấy Profile Mentor
# ==================================================
@mentor_bp.route('/mentor-profile/<string:user_id>', methods=['GET'])
def get_mentor_profile(user_id):
    try:
        engine = get_db_connection()
        with engine.connect() as conn:
            u = conn.execute(text("SELECT username, email FROM users WHERE id = :uid"), {"uid": user_id}).fetchone()
            m = conn.execute(text("SELECT bio, skills FROM mentors WHERE user_id = :uid"), {"uid": user_id}).fetchone()
            
            # Xử lý skills an toàn
            skills_list = []
            if m and m.skills:
                skills_list = [s.strip() for s in str(m.skills).split(',')]

            return jsonify({
                'full_name': u.username if u else "Mentor", 
                'email': u.email if u else '', 
                'bio': m.bio if m else '', 
                'skills': skills_list
            }), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 23. API Cập Nhật Profile
# ==================================================
@mentor_bp.route('/mentor-profile', methods=['PUT'])
def update_mentor_profile():
    try:
        data = request.json
        uid = data.get('user_id')
        if not uid: return jsonify({'error': 'Thieu ID'}), 400

        engine = get_db_connection()
        with engine.connect() as conn:
            # Update bảng users
            conn.execute(text("UPDATE users SET username = :n WHERE id = :uid"), {"n": data['full_name'], "uid": uid})
            # Update bảng mentors
            conn.execute(text("UPDATE mentors SET full_name = :n, bio = :b, skills = :s WHERE user_id = :uid"), 
                         {"n": data['full_name'], "b": data['bio'], "s": data['skills'], "uid": uid})
            conn.commit()
        return jsonify({'message': 'Cap nhat ho so thanh cong'}), 200
    except Exception as e: return jsonify({'error': str(e)}), 500
# ==================================================
# 14. API Quản lý Chủ đề (Topics) - FIX 405/404
# ==================================================
@mentor_bp.route('/topics', methods=['GET', 'POST', 'OPTIONS'])
def manage_topics():
    # Khi nhận lệnh OPTIONS từ trình duyệt, trả về 200 OK ngay để tránh lỗi 405
    if request.method == 'OPTIONS':
        return '', 200

    try:
        engine = get_db_connection()
        
        # Lấy danh sách
        if request.method == 'GET':
            topics = []
            with engine.connect() as conn:
                result = conn.execute(text("SELECT * FROM topics ORDER BY created_at DESC"))
                for row in result:
                    topics.append({
                        'id': row.id,
                        'topic_name': row.topic_name,
                        'level': row.level,
                        'description': row.description
                    })
            return jsonify(topics), 200

        # Thêm mới
        if request.method == 'POST':
            data = request.json
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO topics (topic_name, level, description) 
                    VALUES (:name, :lvl, :desc)
                """), {
                    "name": data['topic_name'],
                    "lvl": data['level'],
                    "desc": data['description']
                })
                conn.commit()
            return jsonify({'message': 'Thêm thành công'}), 201
            
    except Exception as e:
        return jsonify({'error': str(e)}), 500

@mentor_bp.route('/topics/<int:topic_id>', methods=['DELETE', 'OPTIONS'])
def delete_topic_api(topic_id):
    if request.method == 'OPTIONS': return '', 200
    try:
        engine = get_db_connection()
        with engine.connect() as conn:
            conn.execute(text("DELETE FROM topics WHERE id = :tid"), {"tid": topic_id})
            conn.commit()
        return jsonify({'message': 'Đã xóa'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
# API cập nhật trạng thái bài tập
# API cập nhật trạng thái bài tập
@mentor_bp.route('/tasks/<int:task_id>/complete', methods=['PUT'])
def complete_task(task_id):
    try:
        engine = get_db_connection()
        with engine.connect() as conn:
            conn.execute(text("""
                UPDATE tasks 
                SET status = 'Completed' 
                WHERE id = :tid
            """), {"tid": task_id})
            conn.commit()
        return jsonify({'message': 'Task completed'}), 200
    except Exception as e:
        return jsonify({'error': str(e)}), 500
    
# ==============================================================================
# BỔ SUNG: QUẢN LÝ TÀI LIỆU (UPLOAD/DOWNLOAD) & CHẤM ĐIỂM BÀI NÓI (GRADING)
# ==============================================================================

# Cấu hình thư mục lưu trữ file vật lý
UPLOAD_FOLDER = 'static/uploads'
if not os.path.exists(UPLOAD_FOLDER):
    os.makedirs(UPLOAD_FOLDER)

# --- HÀM HỖ TRỢ KẾT NỐI DATABASE XDPM (Dành cho chấm điểm) ---
def get_xdpm_connection():
    engine = get_db_connection()
    # Chuyển đổi URL từ user_db sang xdpm
    db_url = 'mysql+pymysql://root:root@user-db:3306/xdpm?charset=utf8mb4'
    return create_engine(db_url)

# --------------------------------------------------
# 15. API Tải tài liệu lên (Lưu file và ghi Database)
# --------------------------------------------------
@mentor_bp.route('/resources/upload', methods=['POST'])
def upload_resource():
    try:
        if 'file' not in request.files:
            return jsonify({"error": " chưa chọn file kìa!"}), 400
            
        file = request.files['file']
        title = request.form.get('title')
        skill_type = request.form.get('skill_type', 'General')
        description = request.form.get('description', '')
        mentor_id = request.form.get('mentor_id', 'admin-001')

        if file and title:
            # Làm sạch tên file và lưu trữ
            filename = secure_filename(file.filename)
            # Thêm prefix thời gian để không bị trùng tên file
            filename = f"{datetime.now().strftime('%Y%m%d%H%M%S')}_{filename}"
            file_path = os.path.join(UPLOAD_FOLDER, filename)
            file.save(file_path)
            
            # Tự động tính toán thông tin file để khớp với Database
            file_size_kb = os.path.getsize(file_path) / 1024
            file_size_str = f"{round(file_size_kb, 1)} KB" if file_size_kb < 1024 else f"{round(file_size_kb/1024, 1)} MB"
            file_type = filename.rsplit('.', 1)[1].upper() if '.' in filename else 'FILE'
            
            # Link download (Sẽ được gán vào nút Download ở Frontend)
            file_url = f"http://localhost:5002/static/uploads/{filename}"

            engine = get_db_connection()
            with engine.connect() as conn:
                conn.execute(text("""
                    INSERT INTO resources (mentor_id, title, link, file_type, file_size, skill_type, description) 
                    VALUES (:mid, :tit, :lnk, :ft, :fs, :sk, :desc)
                """), {
                    "mid": mentor_id, "tit": title, "lnk": file_url, 
                    "ft": file_type, "fs": file_size_str, "sk": skill_type, "desc": description
                })
                conn.commit()
            
            return jsonify({"message": "Upload thành công!", "url": file_url}), 201
            
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --------------------------------------------------
# 16. API Lấy danh sách bài nói của học viên (Cần chấm điểm)
# --------------------------------------------------
@mentor_bp.route('/grading-list', methods=['GET'])
def get_grading_list():
    try:
        engine = get_xdpm_connection()
        grading_data = []
        with engine.connect() as conn:
            # Lấy các bài thực hành có file ghi âm từ database xdpm
            result = conn.execute(text("""
                SELECT id, user_id, topic, accuracy_score, audio_url, status, created_at 
                FROM practice_sessions 
                WHERE audio_url IS NOT NULL 
                ORDER BY created_at DESC
            """)).fetchall()
            
            for r in result:
                grading_data.append({
                    "id": r.id,
                    "user_id": r.user_id,
                    "topic": r.topic,
                    "ai_score": r.accuracy_score,
                    "audio_url": r.audio_url, # Link để Mentor nghe trực tiếp
                    "status": r.status,
                    "date": r.created_at.strftime('%d/%m/%Y %H:%M')
                })
        return jsonify(grading_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --------------------------------------------------
# 17. API Mentor chấm điểm và nhận xét (Cập nhật xdpm)
# --------------------------------------------------
@mentor_bp.route('/grade-session', methods=['POST'])
def grade_session():
    try:
        data = request.json
        session_id = data.get('session_id')
        score = data.get('mentor_score')
        feedback = data.get('mentor_feedback')

        engine = get_xdpm_connection()
        with engine.connect() as conn:
            conn.execute(text("""
                UPDATE practice_sessions 
                SET mentor_score = :ms, mentor_feedback = :mf, status = 'Graded' 
                WHERE id = :sid
            """), {"ms": score, "mf": feedback, "sid": session_id})
            conn.commit()
            
        return jsonify({"message": "Bảo đã chấm điểm thành công!"}), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
# --------------------------------------------------
# 16. API Lấy danh sách bài nộp (Khớp với Frontend của Bảo)
# --------------------------------------------------
@mentor_bp.route('/submissions/for-mentor/<string:mentor_id>', methods=['GET'])
def get_grading_list_final(mentor_id): 
    try:
        engine = get_xdpm_connection()
        grading_data = []
        with engine.connect() as conn:
            # Chỉ lấy dữ liệu từ bảng practice_sessions (Giống code cũ để tránh lỗi 500)
            query = text("""
                SELECT id, user_id, topic, accuracy_score, audio_url, status, 
                       created_at, mentor_feedback, mentor_score 
                FROM practice_sessions 
                WHERE audio_url IS NOT NULL 
                ORDER BY created_at DESC
            """)
            result = conn.execute(query).fetchall()
            
            for r in result:
                grading_data.append({
                    "id": r.id,
                    "user_id": r.user_id,
                    "username": f"Học viên {r.user_id[:5]}", # Hiện ID thay vì JOIN tên để không bị lỗi
                    "topic": r.topic or "Hội thoại tự do",
                    "ai_score": r.accuracy_score,
                    "audio_url": r.audio_url, 
                    "status": r.status,
                    "mentor_feedback": r.mentor_feedback,
                    "mentor_score": r.mentor_score,
                    "date": r.created_at.strftime('%d/%m/%Y %H:%M') if r.created_at else ""
                })
        return jsonify(grading_data), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# --------------------------------------------------
# 17. API Chấm điểm (Khớp với nút Lưu kết quả)
# --------------------------------------------------
@mentor_bp.route('/submissions/grade', methods=['POST'])
def grade_session_final():
    try:
        data = request.json
        session_id = data.get('submission_id') 
        score = data.get('score')
        comment = data.get('comment')
        learner_id = data.get('learner_id')

        if not session_id:
            return jsonify({"error": "Thiếu ID bài nộp"}), 400

        engine = get_xdpm_connection()
        with engine.connect() as conn:
            # 1. Cập nhật bảng kết quả nói (Database xdpm)
            conn.execute(text("""
                UPDATE practice_sessions 
                SET mentor_score = :ms, mentor_feedback = :mf, status = 'Graded' 
                WHERE id = :sid
            """), {"ms": score, "mf": comment, "sid": session_id})
            
            # 2. Cập nhật bảng Nhiệm vụ (Database user_db/mentor_db) để hiện bên Progress học viên
            # Lưu ý: title = topic giúp map đúng bài tập
            try:
                conn.execute(text("""
                    UPDATE user_db.tasks 
                    SET score = :s, status = 'Hoàn thành' 
                    WHERE learner_id = :lid AND title = :topic
                """), {"s": score, "lid": learner_id, "topic": data.get('topic')})
            except:
                pass # Bỏ qua nếu bảng tasks không nằm trong kết nối này

            conn.commit()
            
        return jsonify({"message": "Lưu điểm thành công!"}), 200
    except Exception as e:
        print(f"Error Submit Grade: {str(e)}")
        return jsonify({"error": str(e)}), 500
# --------------------------------------------------
# API: Học viên nộp bài ghi âm (Audio Upload)
# --------------------------------------------------
# --------------------------------------------------
# API: Học viên nộp bài ghi âm (Audio Upload)
# --------------------------------------------------
import traceback

@mentor_bp.route('/submissions/upload-audio', methods=['POST', 'OPTIONS'])
def upload_learner_audio():
    if request.method == 'OPTIONS':
        return '', 200

    try:
        # 1. Lấy dữ liệu
        if 'audio' not in request.files:
            return jsonify({"error": "No audio file"}), 400
            
        file = request.files['audio']
        user_id = request.form.get('user_id', 'unknown')
        topic = request.form.get('topic', 'General')
        transcript = request.form.get('transcript', '')

        # 2. Định nghĩa thư mục lưu trữ (Sửa lỗi NameError)
        # Đường dẫn tuyệt đối trong container Docker
        record_dir = "/app/static/recordings"
        if not os.path.exists(record_dir):
            os.makedirs(record_dir, mode=0o777, exist_ok=True)

        # 3. Lưu file vật lý
        filename = secure_filename(f"{user_id}_{datetime.now().strftime('%Y%m%d%H%M%S')}.wav")
        file_path = os.path.join(record_dir, filename)
        file.save(file_path)

        # 4. Lưu vào Database xdpm
        audio_url = f"/static/recordings/{filename}"
        engine = get_xdpm_connection()
        with engine.connect() as conn:
            conn.execute(text("""
                INSERT INTO practice_sessions (user_id, topic, audio_url, ai_feedback, status, created_at)
                VALUES (:uid, :topic, :url, :txt, 'Pending', NOW())
            """), {
                "uid": user_id, "topic": topic, "url": audio_url, "txt": transcript
            })
            conn.commit()

        return jsonify({"message": "Lưu thành công", "audio_url": audio_url}), 201
        
    except Exception as e:
        # 🔥 In lỗi chi tiết ra Terminal để Bảo nhìn thấy nguyên nhân thật
        print("🔥 LỖI CHI TIẾT TẠI BACKEND:")
        traceback.print_exc() 
        return jsonify({"error": str(e)}), 500