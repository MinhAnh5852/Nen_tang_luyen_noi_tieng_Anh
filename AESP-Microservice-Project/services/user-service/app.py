import os
from flask import Flask, jsonify, request
from flask_cors import CORS
from flask_jwt_extended import JWTManager
from database import db, init_db
from config import Config
from controllers.auth_controller import auth_bp
from controllers.user_controller import user_bp
from controllers.internal_controller import internal_bp

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    # 1. Khởi tạo Database
    init_db(app)
    
    with app.app_context():
        try:
            from models.user import User, Feedback 
            db.create_all()
            
            # Kiểm tra và đồng bộ cột is_read nếu chưa tồn tại trong MySQL
            try:
                from sqlalchemy import text
                db.session.execute(text("ALTER TABLE feedbacks ADD COLUMN is_read BOOLEAN DEFAULT FALSE"))
                db.session.commit()
            except Exception:
                db.session.rollback()

            print(">>> [MySQL] Database user_db đã sẵn sàng và đồng bộ!")
        except Exception as e:
            print(f">>> [MySQL] Lỗi khởi tạo database: {e}")
    
    # 2. Cấu hình bảo mật & Middleware
    CORS(app, resources={r"/*": {"origins": "*"}})
    jwt = JWTManager(app)

    # 3. ĐĂNG KÝ CÁC BLUEPRINT (QUAN TRỌNG: Phải khớp với Frontend gọi API)
    # Frontend gọi /api/users/auth/register -> Sẽ khớp với Blueprint này
    app.register_blueprint(auth_bp, url_prefix='/api/users/auth') 
    app.register_blueprint(user_bp, url_prefix='/api/users') 
    app.register_blueprint(internal_bp, url_prefix='/api/users/internal')

    # --- 4. CÁC API DÀNH CHO HỆ THỐNG VÀ ADMIN ---

    @app.get("/api/users/health")
    def health():
        return jsonify({"status": "ok", "service": "user-service"}), 200

    @app.get("/api/users/all")
    def get_all_users_direct():
        try:
            from sqlalchemy import text
            sql = text("SELECT id, username, email, role, status, package_name, user_level FROM users ORDER BY created_at DESC")
            result = db.session.execute(sql)
            users = [dict(r._mapping) for r in result]
            return jsonify(users), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.get("/api/users/feedbacks/all")
    def get_all_feedbacks():
        try:
            from models.user import Feedback, User
            feedbacks = db.session.query(
                Feedback.id,
                Feedback.ai_comment.label('content'),
                Feedback.rating, 
                Feedback.sentiment,
                Feedback.created_at,
                Feedback.target_name,
                Feedback.is_read,
                User.email
            ).join(User, Feedback.user_id == User.id).order_by(Feedback.created_at.desc()).all()

            result = []
            for fb in feedbacks:
                result.append({
                    "id": fb.id,
                    "email": fb.email,
                    "target": fb.target_name or "System",
                    "content": fb.content,
                    "sentiment": fb.sentiment,
                    "rating": fb.rating,
                    "date": fb.created_at.strftime("%d/%m/%Y %H:%M"),
                    "is_read": fb.is_read if fb.is_read is not None else False
                })
            return jsonify(result), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    @app.put("/api/users/feedbacks/<int:fb_id>/read")
    def mark_feedback_read(fb_id):
        try:
            from models.user import Feedback
            fb = db.session.get(Feedback, fb_id)
            if not fb:
                return jsonify({"error": "Không tìm thấy phản hồi"}), 404
            fb.is_read = True
            db.session.commit()
            return jsonify({"success": True}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @app.delete("/api/users/feedbacks/<int:fb_id>")
    def delete_feedback(fb_id):
        try:
            from models.user import Feedback
            fb = db.session.get(Feedback, fb_id)
            if not fb:
                return jsonify({"error": "Không tìm thấy"}), 404
            db.session.delete(fb)
            db.session.commit()
            return jsonify({"success": True}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    @app.post("/api/users/feedbacks/reply")
    def reply_feedback():
        data = request.json
        print(f">>> [ADMIN REPLY] To {data.get('email')}: {data.get('message')}")
        return jsonify({"success": True}), 200

    return app

# ĐƯA BIẾN APP RA NGOÀI ĐỂ GUNICORN (DOCKER) CÓ THỂ NHÌN THẤY
app = create_app()

if __name__ == "__main__":
    # Chỉ chạy khi debug local
    app.run(host="0.0.0.0", port=5000, debug=True)