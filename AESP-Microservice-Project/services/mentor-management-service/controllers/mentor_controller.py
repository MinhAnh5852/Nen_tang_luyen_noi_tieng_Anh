# controllers/mentor_controller.py
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import create_engine, text
import json
from datetime import datetime

mentor_bp = Blueprint('mentor', __name__)

# --- HÀM HỖ TRỢ: KẾT NỐI DATABASE ---
def get_db_connection():
    db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    # Ép buộc sử dụng user_db để đồng bộ dữ liệu giữa các service
    if 'mentor_management_db' in db_url:
        db_url = db_url.replace('mentor_management_db', 'user_db')
    
    if not db_url:
        # Cấu hình dự phòng chạy trong Docker network
        db_url = 'mysql+pymysql://root:root@user-db:3306/user_db?charset=utf8mb4'
        
    return create_engine(db_url)

# ==================================================
# 1. API Đăng ký Mentor
# ==================================================
@mentor_bp.route('/', methods=['POST'])
def create_mentor():
    try:
        data = request.json
        if not data.get('user_id'): return jsonify({'error': 'Thieu user_id'}), 400

        skills_str = json.dumps(data.get('skills', [])) if isinstance(data.get('skills'), list) else data.get('skills', '[]')
        
        engine = get_db_connection()
        with engine.connect() as conn:
            check = conn.execute(text("SELECT id FROM mentors WHERE user_id = :uid"), {"uid": data['user_id']}).fetchone()
            if check:
                return jsonify({'error': 'User nay da la Mentor'}), 409
            
            query = text("""
                INSERT INTO mentors (user_id, full_name, bio, skills_json, status) 
                VALUES (:uid, :name, :bio, :skills, 'PENDING')
            """)
            conn.execute(query, {
                "uid": data['user_id'],
                "name": data.get('full_name', ''),
                "bio": data.get('bio', ''),
                "skills": skills_str
            })
            conn.commit()
        return jsonify({'message': 'Dang ky thanh cong'}), 201
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 2. API Lấy danh sách Mentor (Khớp: GET /api/mentors/profiles)
# ==================================================
@mentor_bp.route('/profiles', methods=['GET'])
def get_mentors():
    try:
        engine = get_db_connection()
        mentors = []
        with engine.connect() as conn:
            # Join với bảng users để lấy email cho Admin
            result = conn.execute(text("""
                SELECT m.*, u.email, u.username 
                FROM mentors m 
                JOIN users u ON m.user_id = u.id 
                ORDER BY m.status DESC, m.created_at DESC
            """))
            for row in result:
                mentors.append({
                    'id': row.user_id, # Đổi thành 'id' để khớp JS frontend
                    'username': row.username or row.full_name,
                    'email': row.email,
                    'bio': row.bio,
                    'skills': json.loads(row.skills_json) if row.skills_json else [], 
                    'status': row.status.lower() # Trả về chữ thường để khớp CSS
                })
        return jsonify(mentors), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 3. API Duyệt Mentor (Khớp: POST /api/mentors/verify/<id>)
# ==================================================
@mentor_bp.route('/verify/<string:user_id>', methods=['POST'])
def verify_mentor(user_id):
    try:
        data = request.json
        # Khớp logic handleAction trong quanlimentor.html
        new_status = 'APPROVED' if data.get('action') == 'approve' else 'REJECTED'
        
        engine = get_db_connection()
        with engine.connect() as conn:
            conn.execute(text("UPDATE mentors SET status = :st WHERE user_id = :uid"), 
                         {"st": new_status, "uid": user_id})
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
@mentor_bp.route('/learners-list', methods=['GET'])
def get_learners_list():
    try:
        engine = get_db_connection()
        learners = []
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM users WHERE role = 'learner'"))
            for row in result: 
                learners.append({
                    'id': row.id, 
                    'full_name': row.username or 'No Name', 
                    'email': row.email, 
                    'level': row.user_level, 
                    'status': row.status
                })
        return jsonify(learners), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

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
                "completed_lessons": len(sessions),
                "total_lessons": total_tasks,
                "average_score": avg,
                "recent_history": history
            }), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 8. API Lấy Phản hồi (Khớp: ai_comment)
# ==================================================
@mentor_bp.route('/learner-feedback/<string:learner_id>', methods=['GET'])
def get_learner_feedback(learner_id):
    try:
        engine = get_db_connection()
        feedbacks = []
        with engine.connect() as conn:
            # Query đúng cột ai_comment thay vì content
            result = conn.execute(text("SELECT * FROM feedbacks WHERE learner_id = :lid ORDER BY created_at DESC"), {"lid": learner_id}).fetchall()
            for row in result: 
                feedbacks.append({
                    'comment': row.ai_comment, 
                    'sentiment': row.sentiment, 
                    'date': row.created_at.strftime('%d/%m/%Y %H:%M')
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
# 14. API Tạo Chủ Đề
# ==================================================
@mentor_bp.route('/topics', methods=['POST'])
def create_topic():
    try:
        data = request.json
        engine = get_db_connection()
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO topics (topic_name, level, description) VALUES (:name, :lvl, :desc)"), {"name": data['topic_name'], "lvl": data['level'], "desc": data['description']}); conn.commit()
        return jsonify({'message': 'Tao chu de thanh cong'}), 201
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 15. API Lấy Chủ Đề
# ==================================================
@mentor_bp.route('/topics', methods=['GET'])
def get_topics():
    try:
        engine = get_db_connection()
        topics = []
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM topics ORDER BY created_at DESC"))
            for row in result: topics.append({'id': row.id, 'topic_name': row.topic_name, 'level': row.level})
        return jsonify(topics), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 16. API Giao Chủ Đề
# ==================================================
@mentor_bp.route('/assign-topic', methods=['POST'])
def assign_topic():
    try:
        data = request.json
        engine = get_db_connection()
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO topic_assignments (learner_id, learner_name, topic_name) VALUES (:lid, :lname, :tname)"), {"lid": data['learner_id'], "lname": data['learner_name'], "tname": data['topic_name']})
            conn.commit()
        return jsonify({'message': 'Giao chu de thanh cong'}), 201
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 17. API Lịch sử giao chủ đề
# ==================================================
@mentor_bp.route('/assigned-topics', methods=['GET'])
def get_assigned_topics():
    try:
        engine = get_db_connection()
        assignments = []
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM topic_assignments ORDER BY assigned_at DESC"))
            for row in result: assignments.append({'learner_name': row.learner_name, 'topic_name': row.topic_name, 'date': row.assigned_at.strftime('%d/%m/%Y %H:%M')})
        return jsonify(assignments), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 18. API Lấy Danh Sách Bài Nộp
# ==================================================
@mentor_bp.route('/submissions', methods=['GET'])
def get_submissions():
    try:
        engine = get_db_connection()
        submissions = []
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM submissions ORDER BY submitted_at DESC"))
            for row in result:
                submissions.append({
                    'id': row.id, 'learner_name': row.learner_name, 'task_title': row.task_title, 'audio_link': row.audio_link, 'status': row.status
                })
        return jsonify(submissions), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 19. API CHẤM ĐIỂM
# ==================================================
@mentor_bp.route('/submissions/<int:sub_id>/grade', methods=['PUT'])
def grade_submission(sub_id):
    try:
        data = request.json
        engine = get_db_connection()
        with engine.connect() as conn:
            conn.execute(text("UPDATE submissions SET score = :s, feedback = :f, status = 'Graded' WHERE id = :sid"), {"s": data['score'], "f": data['feedback'], "sid": sub_id})
            conn.commit()
        return jsonify({'message': 'Cham diem thanh cong'}), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 20. API Lấy Cài Đặt
# ==================================================
@mentor_bp.route('/settings/<string:user_id>', methods=['GET'])
def get_settings(user_id):
    try:
        engine = get_db_connection()
        with engine.connect() as conn:
            row = conn.execute(text("SELECT * FROM mentor_settings WHERE user_id = :uid"), {"uid": user_id}).fetchone()
            if row: return jsonify({'theme': row.theme, 'reminder_enabled': bool(row.reminder_enabled), 'reminder_time': row.reminder_time}), 200
            return jsonify({'theme': 'Light', 'reminder_enabled': False, 'reminder_time': '08:00'}), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 21. API Lưu Cài Đặt
# ==================================================
@mentor_bp.route('/settings', methods=['POST'])
def save_settings():
    try:
        data = request.json
        engine = get_db_connection()
        uid = data.get('user_id', 'current_mentor') 
        with engine.connect() as conn:
            conn.execute(text("REPLACE INTO mentor_settings (user_id, theme, reminder_enabled, reminder_time) VALUES (:uid, :th, :re, :rt)"), 
                         { "uid": uid, "th": data.get('theme', 'Light'), "re": 1 if data.get('reminder_enabled') else 0, "rt": data.get('reminder_time', '08:00') })
            conn.commit()
        return jsonify({'message': 'Luu thanh cong'}), 200
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
            m = conn.execute(text("SELECT bio, skills_json FROM mentors WHERE user_id = :uid"), {"uid": user_id}).fetchone()
            return jsonify({
                'full_name': u.username if u else "Mentor", 
                'email': u.email if u else '', 
                'bio': m.bio if m else '', 
                'skills': json.loads(m.skills_json) if (m and m.skills_json) else []
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
        engine = get_db_connection()
        with engine.connect() as conn:
            skills = json.dumps(data['skills'].split(',')) if isinstance(data['skills'], str) else json.dumps(data['skills'])
            conn.execute(text("UPDATE mentors SET full_name = :n, bio = :b, skills_json = :s WHERE user_id = :uid"), 
                         {"n": data['full_name'], "b": data['bio'], "s": skills, "uid": uid})
            conn.commit()
        return jsonify({'message': 'Cap nhat thanh cong'}), 200
    except Exception as e: return jsonify({'error': str(e)}), 500