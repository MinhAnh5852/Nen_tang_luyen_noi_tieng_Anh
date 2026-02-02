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
    
    # Khởi tạo Database
    init_db(app)
    
    with app.app_context():
        try:
            from models.user import User, Feedback 
            db.create_all()
            
            # Kiểm tra và đồng bộ cột is_read nếu chưa tồn tại trong MySQL
            try:
                from sqlalchemy import text
                # Sử dụng execute để thay đổi cấu trúc bảng trực tiếp
                db.session.execute(text("ALTER TABLE feedbacks ADD COLUMN is_read BOOLEAN DEFAULT FALSE"))
                db.session.commit()
            except Exception:
                db.session.rollback() # Bỏ qua nếu cột đã tồn tại

            print(">>> [MySQL] Database user_db đã sẵn sàng và đồng bộ!")
        except Exception as e:
            print(f">>> [MySQL] Lỗi khởi tạo database: {e}")
    
    # Bật CORS để cho phép các dịch vụ khác (như Gateway) truy cập
    CORS(app, resources={r"/*": {"origins": "*"}})
    jwt = JWTManager(app)

    # ĐĂNG KÝ CÁC BLUEPRINT
    app.register_blueprint(auth_bp, url_prefix='/auth') 
    app.register_blueprint(user_bp, url_prefix='/profile')
    app.register_blueprint(internal_bp, url_prefix='/internal')

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "user-service"}), 200

    # 1. API: Lấy danh sách người dùng cho Admin Dashboard
    @app.get("/all")
    def get_all_users_direct():
        try:
            from sqlalchemy import text
            # Lấy thông tin theo đúng cấu trúc bảng users trong init.sql
            sql = text("SELECT id, username, email, role, status, package_name, user_level FROM users ORDER BY created_at DESC")
            result = db.session.execute(sql)
            users = [dict(r._mapping) for r in result]
            return jsonify(users), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # 2. API: Lấy danh sách phản hồi hệ thống (Sửa lỗi 500 Unknown Column Content)
    @app.get("/feedbacks/all")
    def get_all_feedbacks():
        try:
            from models.user import Feedback, User
            # Ánh xạ ai_comment sang 'content' để frontend không bị lỗi hiển thị
            feedbacks = db.session.query(
                Feedback.id,
                Feedback.ai_comment.label('content'), # Lấy dữ liệu từ cột ai_comment thực tế trong DB
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
                    "content": fb.content, # Trả về key 'content' khớp với JavaScript/HTML
                    "sentiment": fb.sentiment,
                    "rating": fb.rating,
                    "date": fb.created_at.strftime("%d/%m/%Y %H:%M"),
                    "is_read": fb.is_read if fb.is_read is not None else False
                })
            return jsonify(result), 200
        except Exception as e:
            print(f">>> [ERROR] Lỗi lấy feedbacks: {e}")
            return jsonify({"error": str(e)}), 500

    # 3. API: Đánh dấu phản hồi đã đọc
    @app.put("/feedbacks/<int:fb_id>/read")
    def mark_feedback_read(fb_id):
        try:
            from models.user import Feedback
            # Sử dụng db.session.get (Chuẩn SQLAlchemy 2.0) để lấy object theo ID
            fb = db.session.get(Feedback, fb_id)
            if not fb:
                return jsonify({"error": "Không tìm thấy phản hồi"}), 404
            fb.is_read = True
            db.session.commit()
            return jsonify({"success": True}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # 4. API: Xóa phản hồi vĩnh viễn
    @app.delete("/feedbacks/<int:fb_id>")
    def delete_feedback(fb_id):
        try:
            from models.user import Feedback
            fb = db.session.get(Feedback, fb_id)
            if not fb:
                return jsonify({"error": "Không tìm thấy phản hồi"}), 404
            db.session.delete(fb)
            db.session.commit()
            return jsonify({"success": True}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # 5. API: Gửi tin nhắn trả lời tới User (Giả lập gửi Email/Thông báo)
    @app.post("/feedbacks/reply")
    def reply_feedback():
        try:
            data = request.json
            email = data.get('email')
            message = data.get('message')
            # Thực tế: Bạn có thể tích hợp dịch vụ gửi Mail tại đây
            print(f">>> [ADMIN REPLY] Gửi tới {email}: {message}")
            return jsonify({"success": True, "message": f"Đã gửi trả lời tới {email}"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app

app = create_app()

if __name__ == "__main__":
    # Chạy trên port 5000 cho User Service
    app.run(host="0.0.0.0", port=5000, debug=True)