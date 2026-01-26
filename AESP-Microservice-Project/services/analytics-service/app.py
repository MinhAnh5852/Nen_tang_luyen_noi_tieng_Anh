from flask import Flask, jsonify
from flask_sqlalchemy import SQLAlchemy
from database import db
import os

app = Flask(__name__)
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

# Import models sau khi db đã init
from models import SystemStat, ActivityLog

# FIX LỖI: Thay thế before_first_request bằng app_context
with app.app_context():
    db.create_all()

@app.route("/summary", methods=["GET"]) # Nginx đã trỏ /api/analytics/ vào đây rồi
def get_summary():
    try:
        stats = SystemStat.query.all()
        summary = {s.key: s.value for s in stats}
        
        # Đảm bảo các chỉ số quan trọng luôn có (để Dashboard không bị lỗi ...)
        result = {
            "total_users": int(summary.get("total_users", 0)),
            "active_mentors": int(summary.get("active_mentors", 0)),
            "total_revenue": float(summary.get("total_revenue", 0.0)),
            "recent_activities": []
        }
        
        # Lấy nhật ký hoạt động
        logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(5).all()
        result["recent_activities"] = [log.message for log in logs]
        
        return jsonify(result)
    except Exception as e:
        return jsonify({"error": str(e)}), 500

if __name__ == "__main__":
    # Port 5003 khớp với Dockerfile và Nginx
    app.run(host="0.0.0.0", port=5003)