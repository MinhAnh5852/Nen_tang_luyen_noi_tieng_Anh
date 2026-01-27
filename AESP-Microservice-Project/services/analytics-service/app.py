from flask import Flask, jsonify, request
from database import db
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from sqlalchemy import func
import os

app = Flask(__name__)

# Cấu hình Database & JWT
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = "AESP_Secret_Key_2026_Trọng" # Phải khớp với User Service

CORS(app)
db.init_app(app)
jwt = JWTManager(app)

# Import Models sau khi db.init_app
from models import SystemStat, ActivityLog, PracticeSession

# API 1: Dành cho Admin (Giữ nguyên chức năng cũ)
@app.route("/summary", methods=["GET"])
def get_summary():
    try:
        stats = SystemStat.query.all()
        summary = {s.key: s.value for s in stats}
        logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(5).all()
        
        return jsonify({
            "total_users": int(summary.get("total_users", 0)),
            "active_mentors": int(summary.get("active_mentors", 0)),
            "total_revenue": float(summary.get("total_revenue", 0.0)),
            "recent_activities": [log.message for log in logs]
        }), 200
    except Exception as e:
        print(f"ERROR Admin Analytics: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

# API 2: DÀNH CHO LEARNER DASHBOARD (MỚI)
@app.route("/my-progress", methods=["GET"])
@jwt_required()
def get_my_progress():
    try:
        user_id = get_jwt_identity()

        # 1. Tính tổng thời gian luyện tập (SUM duration_seconds)
        total_seconds = db.session.query(func.sum(PracticeSession.duration_seconds))\
            .filter(PracticeSession.user_id == user_id).scalar() or 0
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        time_str = f"{hours}h {minutes}m"

        # 2. Tính độ chính xác trung bình (AVG accuracy_score)
        avg_accuracy = db.session.query(func.avg(PracticeSession.accuracy_score))\
            .filter(PracticeSession.user_id == user_id).scalar() or 0

        # 3. Giả lập Streak và Lesson (Để hiện Dashboard đẹp)
        # Phần này Trọng có thể query thêm từ bảng users nếu cần
        return jsonify({
            "total_time": time_str,
            "accuracy": round(avg_accuracy, 1),
            "lessons_completed": 12, # Demo
            "streak": 15,            # Demo
            "ai_suggestion": "Phát âm của bạn rất tốt, hãy thử luyện thêm chủ đề 'Job Interview' nhé!"
        }), 200

    except Exception as e:
        print(f"ERROR Learner Analytics: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)