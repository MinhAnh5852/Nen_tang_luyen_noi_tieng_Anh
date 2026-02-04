# analytics-service/app.py
from flask import Flask, jsonify, request
from database import db
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from sqlalchemy import func
import os

app = Flask(__name__)

# --- CẤU HÌNH HỆ THỐNG ---
# Luôn lấy từ biến môi trường để đồng bộ với các service khác
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# 🔥 QUAN TRỌNG: Lấy đúng Secret Key từ .env (Không ghi đè giá trị mặc định sai vào đây)
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY')

# 🔥 DÒNG NÀY PHẢI ĐẶT TRƯỚC KHI KHỞI TẠO JWTManager
app.config['JWT_IDENTITY_CLAIM'] = 'user_id' 

CORS(app)
db.init_app(app)
jwt = JWTManager(app)

# Import Models sau khi db đã init
from models import SystemStat, ActivityLog, PracticeSession

# ---------------------------------------------------------
# API 1: DÀNH CHO ADMIN DASHBOARD
# ---------------------------------------------------------
@app.route("/api/analytics/summary", methods=["GET"])
def get_summary():
    try:
        stats = SystemStat.query.all()
        summary = {s.key: s.value for s in stats}
        
        try:
            logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(5).all()
            recent_activities = [log.message for log in logs]
        except Exception:
            recent_activities = []

        return jsonify({
            "total_users": int(summary.get("total_users", 0)),
            "active_mentors": int(summary.get("active_mentors", 0)),
            "total_revenue": float(summary.get("total_revenue", 0.0)),
            "recent_activities": recent_activities
        }), 200
    except Exception as e:
        print(f"Lỗi Admin Analytics: {e}")
        return jsonify({"error": str(e)}), 500

# ---------------------------------------------------------
# API 2: DÀNH CHO LEARNER DASHBOARD (Dữ liệu cá nhân)
# ---------------------------------------------------------
@app.route("/api/analytics/summary/<string:user_id>", methods=["GET"])
@app.route("/api/analytics/detailed/<string:user_id>", methods=["GET"])
@jwt_required()
def get_learner_summary(user_id):
    try:
        # Lấy identity từ token để đảm bảo an toàn (tùy chọn so sánh với user_id truyền vào)
        # current_user_id = get_jwt_identity()

        # Tính toán dữ liệu thực tế từ bảng PracticeSession
        total_seconds = db.session.query(func.sum(PracticeSession.duration_seconds))\
            .filter(PracticeSession.user_id == user_id).scalar() or 0
        
        avg_accuracy = db.session.query(func.avg(PracticeSession.accuracy_score))\
            .filter(PracticeSession.user_id == user_id).scalar() or 0
            
        lessons = db.session.query(func.count(PracticeSession.id))\
            .filter(PracticeSession.user_id == user_id).scalar() or 0

        return jsonify({
            "total_time": f"{total_seconds // 3600}h {(total_seconds % 3600) // 60}m",
            "accuracy": round(float(avg_accuracy), 1),
            "lessons_completed": lessons,
            "streak": 1, 
            "ai_suggestion": "Hãy tiếp tục luyện tập để cải thiện kỹ năng nhé!",
            "weekly_activity": [
                {"day": "T2", "hours": 1.5}, {"day": "T3", "hours": 2}, 
                {"day": "T4", "hours": 0.5}, {"day": "T5", "hours": 3}
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
@app.route("/api/analytics/learner/<string:user_id>", methods=["GET"])
@jwt_required()
def get_mentor_learner_stats(user_id):
    try:
        # Lấy tất cả bài tập của học viên đó
        sessions = PracticeSession.query.filter_by(user_id=user_id).order_by(PracticeSession.created_at.desc()).all()
        
        if not sessions:
            return jsonify({
                "average_score": 0, "completed_lessons": 0, "total_lessons": 30,
                "last_active": "Chưa có dữ liệu",
                "skills": {"speaking": 0, "listening": 0, "vocabulary": 0},
                "recent_history": []
            }), 200

        # Tính toán điểm trung bình để vẽ biểu đồ
        avg_acc = sum(s.accuracy_score for s in sessions) / len(sessions)
        avg_gram = sum(s.grammar_score for s in sessions) / len(sessions)
        avg_vocab = sum(s.vocabulary_score for s in sessions) / len(sessions)

        return jsonify({
            "average_score": round(avg_acc / 10, 1), # Chuyển thang 100 về thang 10
            "completed_lessons": len(sessions),
            "total_lessons": 30,
            "last_active": sessions[0].created_at.strftime("%d/%m/%Y"),
            "skills": {
                "speaking": round(avg_acc, 0),
                "listening": round(avg_gram, 0),
                "vocabulary": round(avg_vocab, 0)
            },
            "recent_history": [
                {"date": s.created_at.strftime("%d/%m/%Y"), "lesson": s.topic, "score": s.accuracy_score} 
                for s in sessions[:5]
            ]
        }), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)