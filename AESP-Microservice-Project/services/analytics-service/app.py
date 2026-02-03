from flask import Flask, jsonify, request
from database import db
from flask_jwt_extended import JWTManager, jwt_required, get_jwt_identity
from flask_cors import CORS
from sqlalchemy import func
import os

app = Flask(__name__)

# Cấu hình Database & JWT
# Trọng kiểm tra file .env xem DATABASE_URL đã đúng chưa nhé (mysql+pymysql://...)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False
app.config['JWT_SECRET_KEY'] = os.environ.get('JWT_SECRET_KEY', "AESP_Secret_Key_2026_Trong") 

CORS(app)
db.init_app(app)
jwt = JWTManager(app)

# Import Models
from models import SystemStat, ActivityLog, PracticeSession

# ---------------------------------------------------------
# API 1: DÀNH CHO ADMIN DASHBOARD (Fix lỗi 500)
# ---------------------------------------------------------
@app.route("/api/analytics/summary", methods=["GET"])
def get_summary():
    try:
        # 1. Lấy tất cả stats. Nếu bảng trống, stats sẽ là danh sách rỗng
        stats = SystemStat.query.all()
        summary = {s.key: s.value for s in stats}
        
        # 2. Lấy logs. Dùng try-except riêng để nếu bảng logs lỗi, stats vẫn hiện
        try:
            logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(5).all()
            recent_activities = [log.message for log in logs]
        except Exception as log_err:
            print(f"Bảng ActivityLog chưa có dữ liệu: {log_err}")
            recent_activities = []

        # 3. Trả về dữ liệu kèm ép kiểu an toàn (Safe casting)
        return jsonify({
            "total_users": int(summary.get("total_users", 0)),
            "active_mentors": int(summary.get("active_mentors", 0)),
            "total_revenue": float(summary.get("total_revenue", 0.0)),
            "recent_activities": recent_activities
        }), 200

    except Exception as e:
        # Dòng này cực kỳ quan trọng để Trọng check log trong Docker
        print(f"CỰC KÌ NGUY HIỂM - Lỗi Admin Analytics: {e}")
        return jsonify({
            "error": "Internal Server Error",
            "message": str(e)  # Hiện lỗi ra để Trọng dễ debug
        }), 500

# ---------------------------------------------------------
# API 2: DÀNH CHO LEARNER DASHBOARD (Dữ liệu cá nhân)
# ---------------------------------------------------------
@app.route("/my-progress", methods=["GET"])
@jwt_required()
def get_my_progress():
    try:
        user_id = get_jwt_identity()

        # 1. Tính tổng thời gian luyện tập (An toàn với scalar)
        total_seconds = db.session.query(func.sum(PracticeSession.duration_seconds))\
            .filter(PracticeSession.user_id == user_id).scalar() or 0
        
        hours = total_seconds // 3600
        minutes = (total_seconds % 3600) // 60
        time_str = f"{hours}h {minutes}m"

        # 2. Tính độ chính xác trung bình
        avg_accuracy = db.session.query(func.avg(PracticeSession.accuracy_score))\
            .filter(PracticeSession.user_id == user_id).scalar() or 0

        return jsonify({
            "total_time": time_str,
            "accuracy": round(float(avg_accuracy), 1),
            "lessons_completed": 12, # Demo - Có thể query count Lesson sau
            "streak": 15,            # Demo
            "ai_suggestion": "Phát âm của bạn rất tốt, hãy luyện thêm chủ đề 'Job Interview' nhé!"
        }), 200

    except Exception as e:
        print(f"Lỗi Learner Analytics: {e}")
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Port 5003 phải khớp với file nginx.conf của Trọng
    app.run(host="0.0.0.0", port=5003)