# controllers/mentor_controller.py
from flask import Blueprint, request, jsonify, current_app
from sqlalchemy import create_engine, text
import json

mentor_bp = Blueprint('mentor', __name__)

# --- HÀM HỖ TRỢ: LUÔN KẾT NỐI VÀO USER_DB ---
def get_db_connection():
    # Lấy chuỗi kết nối từ cấu hình ứng dụng
    db_url = current_app.config.get('SQLALCHEMY_DATABASE_URI', '')
    
    # Ép buộc sử dụng user_db thay vì các database cũ để đảm bảo đồng bộ
    if 'mentor_management_db' in db_url:
        db_url = db_url.replace('mentor_management_db', 'user_db')
    
    # Cấu hình dự phòng nếu chuỗi kết nối trống
    if not db_url:
        db_url = 'mysql+pymysql://root:@localhost:3307/user_db'
        
    return create_engine(db_url)

# ==================================================
# 1. API Đăng ký Mentor
# ==================================================
@mentor_bp.route('/api/mentors', methods=['POST'])
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
# 2. API Lấy danh sách Mentor
# ==================================================
@mentor_bp.route('/api/mentors', methods=['GET'])
def get_mentors():
    try:
        engine = get_db_connection()
        mentors = []
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM mentors ORDER BY status DESC, created_at DESC"))
            for row in result:
                mentors.append({
                    'user_id': row.user_id,
                    'full_name': row.full_name,
                    'bio': row.bio,
                    'skills': row.skills_json, 
                    'status': row.status
                })
        return jsonify(mentors), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 3. API Duyệt Mentor
# ==================================================
@mentor_bp.route('/api/mentors/<string:user_id>/approve', methods=['PUT'])
def approve_mentor(user_id):
    try:
        engine = get_db_connection()
        with engine.connect() as conn:
            conn.execute(text("UPDATE mentors SET status = 'APPROVED' WHERE user_id = :uid"), {"uid": user_id})
            conn.commit()
        return jsonify({'message': 'Da duyet thanh cong'}), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 4. API Xóa Mentor
# ==================================================
@mentor_bp.route('/api/mentors/<string:user_id>', methods=['DELETE'])
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
@mentor_bp.route('/api/learners-list', methods=['GET'])
def get_learners_list():
    try:
        engine = get_db_connection()
        learners = []
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM users WHERE role = 'learner' OR role = 'LEARNER'"))
            for row in result: 
                learners.append({
                    'id': row.id, 
                    'full_name': getattr(row, 'username', getattr(row, 'full_name', 'No Name')), 
                    'email': row.email, 
                    'level': getattr(row, 'user_level', 'Beginner'), 
                    'status': getattr(row, 'status', 'active')
                })
        return jsonify(learners), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 6. API Gửi tin nhắn
# ==================================================
@mentor_bp.route('/api/messages', methods=['POST'])
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
# 7. API Lấy Tiến Độ (ĐỒNG BỘ DỮ LIỆU THẬT)
# ==================================================
@mentor_bp.route('/api/learner-progress/<string:learner_id>', methods=['GET'])
def get_learner_progress(learner_id):
    try:
        engine = get_db_connection()
        with engine.connect() as conn:
            # Lấy danh sách bài đã học (có điểm)
            sessions = conn.execute(text("SELECT * FROM learning_sessions WHERE learner_id = :lid AND score > 0 ORDER BY created_at DESC"), {"lid": learner_id}).fetchall()
            
            # Lấy tổng số bài đã giao từ bảng tasks (Để làm mục tiêu)
            total_tasks = conn.execute(text("SELECT COUNT(*) FROM tasks WHERE learner_id = :lid"), {"lid": learner_id}).scalar() or 10
            
            if not sessions:
                return jsonify({
                    "completed_lessons": 0, "total_lessons": total_tasks, "average_score": 0, 
                    "skills": {"speaking": 0, "listening": 0, "vocabulary": 0}, "recent_history": []
                }), 200

            total_score = sum(s.score for s in sessions)
            avg = round(total_score / len(sessions), 1)
            
            history = [{"date": s.created_at.strftime('%d/%m/%Y'), "lesson": s.lesson_name, "score": s.score} for s in sessions[:5]]
            
            return jsonify({
                "completed_lessons": len(sessions),
                "total_lessons": total_tasks,
                "average_score": avg,
                "last_active": sessions[0].created_at.strftime('%Y-%m-%d'),
                "skills": {"speaking": int(avg*10), "listening": 75, "vocabulary": 70}, # Ví dụ skill dựa theo điểm
                "recent_history": history
            }), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 8. API Lấy Phản hồi AI
# ==================================================
@mentor_bp.route('/api/learner-feedback/<string:learner_id>', methods=['GET'])
def get_learner_feedback(learner_id):
    try:
        engine = get_db_connection()
        feedbacks = []
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM feedbacks WHERE learner_id = :lid ORDER BY created_at DESC"), {"lid": learner_id}).fetchall()
            for row in result: feedbacks.append({'comment': row.ai_comment, 'sentiment': row.sentiment, 'date': row.created_at.strftime('%d/%m/%Y %H:%M')})
        return jsonify(feedbacks), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 9. API Tạo bài tập (ĐỒNG BỘ: Cập nhật mục tiêu tiến độ)
# ==================================================
@mentor_bp.route('/api/tasks', methods=['POST'])
def create_task():
    try:
        data = request.json
        engine = get_db_connection()
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO tasks (learner_id, learner_name, title, description, deadline, status) VALUES (:lid, :lname, :tit, :desc, :dead, 'Pending')"), 
                         {"lid": data['learner_id'], "lname": data['learner_name'], "tit": data['title'], "desc": data['description'], "dead": data['deadline']})
            conn.commit()
        return jsonify({'message': 'Giao bài và cập nhật tiến độ thành công'}), 201
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 10. API Lấy bài tập
# ==================================================
@mentor_bp.route('/api/tasks', methods=['GET'])
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
# 11. API Xếp Hạng (DỰA TRÊN ĐIỂM THẬT)
# ==================================================
@mentor_bp.route('/api/rankings', methods=['GET'])
def get_rankings():
    try:
        engine = get_db_connection()
        ranking_data = []
        with engine.connect() as conn:
            # Query tính điểm trung bình từ bảng học tập
            query = text("""
                SELECT u.username as name, ROUND(AVG(ls.score), 2) as avg_score, COUNT(ls.id) as total_lessons, u.id
                FROM users u
                JOIN learning_sessions ls ON u.id = ls.learner_id
                WHERE ls.score > 0
                GROUP BY u.id
                ORDER BY avg_score DESC
            """)
            result = conn.execute(query).fetchall()
            for r in result:
                ranking_data.append({'id': r.id, 'name': r.name, 'avg_score': r.avg_score, 'total_lessons': r.total_lessons})
        return jsonify(ranking_data), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 12. API Tạo Tài Liệu
# ==================================================
@mentor_bp.route('/api/resources', methods=['POST'])
def create_resource():
    try:
        data = request.json
        engine = get_db_connection()
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO resources (title, link, skill_type, description) VALUES (:tit, :lnk, :sk, :desc)"), {"tit": data['title'], "lnk": data['link'], "sk": data['skill_type'], "desc": data['description']})
            conn.commit()
        return jsonify({'message': 'Them tai lieu thanh cong'}), 201
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 13. API Lấy Tài Liệu
# ==================================================
@mentor_bp.route('/api/resources', methods=['GET'])
def get_resources():
    try:
        engine = get_db_connection()
        resources = []
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM resources ORDER BY created_at DESC"))
            for row in result: resources.append({'id': row.id, 'title': row.title, 'link': row.link, 'skill_type': row.skill_type, 'description': row.description, 'date': row.created_at.strftime('%d/%m/%Y')})
        return jsonify(resources), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 14. API Tạo Chủ Đề
# ==================================================
@mentor_bp.route('/api/topics', methods=['POST'])
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
@mentor_bp.route('/api/topics', methods=['GET'])
def get_topics():
    try:
        engine = get_db_connection()
        topics = []
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM topics ORDER BY created_at DESC"))
            for row in result: topics.append({'id': row.id, 'topic_name': row.topic_name, 'level': row.level, 'description': row.description})
        return jsonify(topics), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 16. API Giao Chủ Đề (ĐỒNG BỘ: Tạo phiên học mới)
# ==================================================
@mentor_bp.route('/api/assign-topic', methods=['POST'])
def assign_topic():
    try:
        data = request.json
        engine = get_db_connection()
        with engine.connect() as conn:
            conn.execute(text("INSERT INTO topic_assignments (learner_id, learner_name, topic_name) VALUES (:lid, :lname, :tname)"), {"lid": data['learner_id'], "lname": data['learner_name'], "tname": data['topic_name']})
            # Đồng bộ sang học tập
            conn.execute(text("INSERT INTO learning_sessions (learner_id, lesson_name, skill_type, score, status) VALUES (:lid, :name, 'Speaking', 0, 'In Progress')"), 
                         {"lid": data['learner_id'], "name": f"Chủ đề: {data['topic_name']}"})
            conn.commit()
        return jsonify({'message': 'Giao chu de thanh cong'}), 201
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 17. API Lịch sử giao chủ đề
# ==================================================
@mentor_bp.route('/api/assigned-topics', methods=['GET'])
def get_assigned_topics():
    try:
        engine = get_db_connection()
        assignments = []
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM topic_assignments ORDER BY assigned_at DESC LIMIT 10"))
            for row in result: assignments.append({'id': row.id, 'learner_name': row.learner_name, 'topic_name': row.topic_name, 'date': row.assigned_at.strftime('%d/%m/%Y %H:%M')})
        return jsonify(assignments), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 18. API Lấy Danh Sách Bài Nộp
# ==================================================
@mentor_bp.route('/api/submissions', methods=['GET'])
def get_submissions():
    try:
        engine = get_db_connection()
        submissions = []
        with engine.connect() as conn:
            result = conn.execute(text("SELECT * FROM submissions ORDER BY submitted_at DESC"))
            for row in result:
                submissions.append({
                    'id': row.id, 'learner_name': row.learner_name, 'task_title': row.task_title, 'audio_link': row.audio_link, 'score': row.score, 'feedback': row.feedback, 'status': row.status, 'date': row.submitted_at.strftime('%d/%m/%Y %H:%M')
                })
        return jsonify(submissions), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 19. API CHẤM ĐIỂM (ĐỒNG BỘ: Cập nhật TIẾN ĐỘ & XẾP HẠNG)
# ==================================================
@mentor_bp.route('/api/submissions/<int:sub_id>/grade', methods=['PUT'])
def grade_submission(sub_id):
    try:
        data = request.json
        engine = get_db_connection()
        with engine.connect() as conn:
            sub = conn.execute(text("SELECT * FROM submissions WHERE id = :sid"), {"sid": sub_id}).fetchone()
            if not sub: return jsonify({'error': 'Ko tim thay'}), 404
            
            # 1. Cập nhật bảng nộp bài
            conn.execute(text("UPDATE submissions SET score = :s, feedback = :f, status = 'Graded' WHERE id = :sid"), {"s": data['score'], "f": data['feedback'], "sid": sub_id})
            
            # 2. ĐỒNG BỘ: Chèn kết quả vào bảng học tập (learning_sessions)
            conn.execute(text("""
                INSERT INTO learning_sessions (learner_id, lesson_name, skill_type, score, status, created_at) 
                VALUES (:lid, :name, 'Speaking', :score, 'Completed', NOW())
            """), {"lid": sub.learner_id, "name": f"Chấm điểm: {sub.task_title}", "score": data['score']})
            
            conn.commit()
        return jsonify({'message': 'Cham diem va dong bo thanh cong'}), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 20. API Lấy Cài Đặt
# ==================================================
@mentor_bp.route('/api/settings/<string:user_id>', methods=['GET'])
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
@mentor_bp.route('/api/settings', methods=['POST'])
def save_settings():
    try:
        data = request.json
        engine = get_db_connection()
        uid = data.get('user_id', 'current_mentor') 
        with engine.connect() as conn:
            check = conn.execute(text("SELECT id FROM mentor_settings WHERE user_id = :uid"), {"uid": uid}).fetchone()
            if check:
                query = text("UPDATE mentor_settings SET theme = :th, reminder_enabled = :re, reminder_time = :rt WHERE user_id = :uid")
            else:
                query = text("INSERT INTO mentor_settings (user_id, theme, reminder_enabled, reminder_time) VALUES (:uid, :th, :re, :rt)")
            conn.execute(query, { "uid": uid, "th": data.get('theme', 'Light'), "re": 1 if data.get('reminder_enabled') else 0, "rt": data.get('reminder_time', '08:00') })
            conn.commit()
        return jsonify({'message': 'Luu thanh cong'}), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 22. API Lấy Profile Mentor
# ==================================================
@mentor_bp.route('/api/mentor-profile/<string:user_id>', methods=['GET'])
def get_mentor_profile(user_id):
    try:
        engine = get_db_connection()
        with engine.connect() as conn:
            u = conn.execute(text("SELECT * FROM users WHERE id = :uid"), {"uid": user_id}).fetchone()
            m = conn.execute(text("SELECT * FROM mentors WHERE user_id = :uid"), {"uid": user_id}).fetchone()
            full_name = getattr(u, 'username', getattr(u, 'full_name', 'Mentor')) if u else "Mentor"
            skills = json.loads(m.skills_json) if (m and m.skills_json) else []
            return jsonify({'full_name': full_name, 'email': u.email if u else '', 'bio': m.bio if m else '', 'skills': skills}), 200
    except Exception as e: return jsonify({'error': str(e)}), 500

# ==================================================
# 23. API Cập Nhật Profile
# ==================================================
@mentor_bp.route('/api/mentor-profile', methods=['PUT'])
def update_mentor_profile():
    try:
        data = request.json
        uid = data.get('user_id')
        engine = get_db_connection()
        with engine.connect() as conn:
            check = conn.execute(text("SELECT id FROM mentors WHERE user_id = :uid"), {"uid": uid}).fetchone()
            skills = json.dumps(data['skills'].split(',')) if isinstance(data['skills'], str) else json.dumps(data['skills'])
            if check:
                conn.execute(text("UPDATE mentors SET full_name = :n, bio = :b, skills_json = :s WHERE user_id = :uid"), {"n": data['full_name'], "b": data['bio'], "s": skills, "uid": uid})
            else:
                conn.execute(text("INSERT INTO mentors (user_id, full_name, bio, skills_json, status) VALUES (:uid, :n, :b, :s, 'APPROVED')"), {"uid": uid, "n": data['full_name'], "b": data['bio'], "s": skills})
            conn.commit()
        return jsonify({'message': 'Cap nhat thanh cong'}), 200
    except Exception as e: return jsonify({'error': str(e)}), 500