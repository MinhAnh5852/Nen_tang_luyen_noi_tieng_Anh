from flask import Flask, jsonify
from database import db
import os

app = Flask(__name__)
# Đảm bảo DATABASE_URL trong docker-compose là analytics_db
app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

db.init_app(app)

from models import SystemStat, ActivityLog

# Khởi tạo Database và dữ liệu mẫu
with app.app_context():
    db.create_all()
    # Tự động chèn các row nếu chưa có để Dashboard không bị lỗi
    for k in ['total_users', 'active_mentors', 'total_revenue']:
        if not SystemStat.query.get(k):
            db.session.add(SystemStat(key=k, value=0))
    db.session.commit()

@app.route("/summary", methods=["GET"])
def get_summary():
    try:
        stats = SystemStat.query.all()
        summary = {s.key: s.value for s in stats}
        
        # Lấy 5 log hoạt động gần nhất
        logs = ActivityLog.query.order_by(ActivityLog.created_at.desc()).limit(5).all()
        
        return jsonify({
            "total_users": int(summary.get("total_users", 0)),
            "active_mentors": int(summary.get("active_mentors", 0)),
            "total_revenue": float(summary.get("total_revenue", 0.0)),
            "recent_activities": [log.message for log in logs]
        }), 200
    except Exception as e:
        # In log ra docker console để dễ debug
        print(f"ERROR Analytics: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5003)