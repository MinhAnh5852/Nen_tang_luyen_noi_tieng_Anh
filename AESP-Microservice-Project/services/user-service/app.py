# import os
# from flask import Flask, jsonify, request
# from flask_cors import CORS
# from flask_jwt_extended import JWTManager
# from database import db, init_db
# from config import Config
# from controllers.auth_controller import auth_bp
# from controllers.user_controller import user_bp
# from controllers.internal_controller import internal_bp

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)
    
#     init_db(app)
    
#     with app.app_context():
#         try:
#             from models.user import User, Feedback 
#             db.create_all()
#             print(">>> [MySQL] Database đã sẵn sàng!")
#         except Exception as e:
#             print(f">>> [MySQL] Lỗi khởi tạo: {e}")
    
#     CORS(app, resources={r"/*": {"origins": "*"}})
#     jwt = JWTManager(app)

#     # ĐĂNG KÝ BLUEPRINT: Sửa prefix để khớp với Nginx
#     # Nếu Nginx config là location /api/users/ { proxy_pass ... }
#     # Thì các route trong auth_bp sẽ bắt đầu bằng /auth/...
#     app.register_blueprint(auth_bp, url_prefix='/auth') 
#     app.register_blueprint(user_bp, url_prefix='/profile')
#     app.register_blueprint(internal_bp, url_prefix='/internal')

#     @app.get("/health")
#     def health():
#         return jsonify({"status": "ok", "service": "user-service"}), 200

#     # ROUTE QUAN TRỌNG: Phục vụ trang Admin Dashboard
#     # Trình duyệt gọi: /api/users/all -> Nginx -> /all
#     @app.get("/all")
#     def get_all_users_direct():
#         try:
#             from sqlalchemy import text
#             # Thêm username và status vào câu lệnh SQL
#             sql = text("SELECT id, username, email, role, status FROM users ORDER BY id DESC")
#             result = db.session.execute(sql)
#             users = [dict(r._mapping) for r in result]
#             return jsonify(users), 200
#         except Exception as e:
#             print(f"Lỗi truy vấn SQL: {e}")
#             return jsonify({"error": str(e)}), 500

#     return app
    
# app = create_app()

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)
# import os
# from flask import Flask, jsonify, request
# from flask_cors import CORS
# from flask_jwt_extended import JWTManager
# from database import db, init_db
# from config import Config
# from controllers.auth_controller import auth_bp
# from controllers.user_controller import user_bp
# from controllers.internal_controller import internal_bp

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)
    
#     init_db(app)
    
#     with app.app_context():
#         try:
#             from models.user import User, Feedback 
#             db.create_all()
#             print(">>> [MySQL] Database đã sẵn sàng!")
#         except Exception as e:
#             print(f">>> [MySQL] Lỗi khởi tạo: {e}")
    
#     CORS(app, resources={r"/*": {"origins": "*"}})
#     jwt = JWTManager(app)

#     # ĐĂNG KÝ BLUEPRINT
#     app.register_blueprint(auth_bp, url_prefix='/auth') 
#     app.register_blueprint(user_bp, url_prefix='/profile')
#     app.register_blueprint(internal_bp, url_prefix='/internal')

#     @app.get("/health")
#     def health():
#         return jsonify({"status": "ok", "service": "user-service"}), 200

#     # ROUTE: Lấy danh sách user
#     @app.get("/all")
#     def get_all_users_direct():
#         try:
#             from sqlalchemy import text
#             sql = text("SELECT id, username, email, role, status FROM users ORDER BY id DESC")
#             result = db.session.execute(sql)
#             users = [dict(r._mapping) for r in result]
#             return jsonify(users), 200
#         except Exception as e:
#             return jsonify({"error": str(e)}), 500

#     # --- ROUTE MỚI: Nằm bên trong hàm create_app để app nhận diện được ---
#     @app.get("/feedbacks/all")
#     def get_all_feedbacks():
#         try:
#             from models.user import Feedback, User
#             # Join với bảng User để lấy email người gửi
#             feedbacks = db.session.query(
#                 Feedback.content, 
#                 Feedback.rating, 
#                 Feedback.created_at,
#                 Feedback.target_name,
#                 User.email
#             ).join(User, Feedback.user_id == User.id).order_by(Feedback.created_at.desc()).all()

#             result = []
#             for fb in feedbacks:
#                 result.append({
#                     "email": fb.email,
#                     "target": fb.target_name,
#                     "content": fb.content,
#                     "rating": fb.rating,
#                     "date": fb.created_at.strftime("%d/%m/%Y")
#                 })
#             return jsonify(result), 200
#         except Exception as e:
#             print(f"Lỗi lấy feedbacks: {e}")
#             return jsonify({"error": str(e)}), 500

#     return app

# # Khởi tạo app
# app = create_app()

# if __name__ == "__main__":
#     app.run(host="0.0.0.0", port=5000, debug=True)

# import os
# from flask import Flask, jsonify, request
# from flask_cors import CORS
# from flask_jwt_extended import JWTManager
# from database import db, init_db
# from config import Config
# from controllers.auth_controller import auth_bp
# from controllers.user_controller import user_bp
# from controllers.internal_controller import internal_bp

# def create_app():
#     app = Flask(__name__)
#     app.config.from_object(Config)
    
#     init_db(app)
    
#     with app.app_context():
#         try:
#             from models.user import User, Feedback 
#             db.create_all()
#             print(">>> [MySQL] Database đã sẵn sàng!")
#         except Exception as e:
#             print(f">>> [MySQL] Lỗi khởi tạo: {e}")
    
#     CORS(app, resources={r"/*": {"origins": "*"}})
#     jwt = JWTManager(app)

#     # ĐĂNG KÝ BLUEPRINT
#     app.register_blueprint(auth_bp, url_prefix='/auth') 
#     app.register_blueprint(user_bp, url_prefix='/profile')
#     app.register_blueprint(internal_bp, url_prefix='/internal')

#     @app.get("/health")
#     def health():
#         return jsonify({"status": "ok", "service": "user-service"}), 200

#     # ROUTE: Lấy danh sách user cho Dashboard
#     @app.get("/all")
#     def get_all_users_direct():
#         try:
#             from sqlalchemy import text
#             sql = text("SELECT id, username, email, role, status FROM users ORDER BY id DESC")
#             result = db.session.execute(sql)
#             users = [dict(r._mapping) for r in result]
#             return jsonify(users), 200
#         except Exception as e:
#             return jsonify({"error": str(e)}), 500

#     # 1. API: Lấy danh sách phản hồi (Đã bổ sung ID để xóa/ẩn)
#     @app.get("/feedbacks/all")
#     def get_all_feedbacks():
#         try:
#             from models.user import Feedback, User
#             # Join lấy ID của feedback để phục vụ chức năng xóa
#             feedbacks = db.session.query(
#                 Feedback.id,
#                 Feedback.content, 
#                 Feedback.rating, 
#                 Feedback.created_at,
#                 Feedback.target_name,
#                 User.email
#             ).join(User, Feedback.user_id == User.id).order_by(Feedback.created_at.desc()).all()

#             result = []
#             for fb in feedbacks:
#                 result.append({
#                     "id": fb.id,
#                     "email": fb.email,
#                     "target": fb.target_name,
#                     "content": fb.content,
#                     "rating": fb.rating,
#                     "date": fb.created_at.strftime("%d/%m/%Y")
#                 })
#             return jsonify(result), 200
#         except Exception as e:
#             print(f"Lỗi lấy feedbacks: {e}")
#             return jsonify({"error": str(e)}), 500

#     # 2. API: Xóa phản hồi vĩnh viễn
#     @app.delete("/feedbacks/<int:fb_id>")
#     def delete_feedback(fb_id):
#         try:
#             from models.user import Feedback
#             fb = Feedback.query.get(fb_id)
#             if not fb:
#                 return jsonify({"error": "Không tìm thấy phản hồi"}), 404
#             db.session.delete(fb)
#             db.session.commit()
#             return jsonify({"success": True, "message": "Đã xóa thành công"}), 200
#         except Exception as e:
#             db.session.rollback()
#             return jsonify({"error": str(e)}), 500

#     # 3. API: Gửi phản hồi ngược lại cho User (Mockup gửi trả lời)
#     @app.post("/feedbacks/reply")
#     def reply_feedback():
#         try:
#             data = request.json
#             email = data.get('email')
#             message = data.get('message')
#             # Tại đây bạn có thể thêm logic gửi Email thực tế
#             print(f">>> [REPLY] Gửi tới {email}: {message}")
#             return jsonify({"success": True, "message": f"Đã gửi trả lời tới {email}"}), 200
#         except Exception as e:
#             return jsonify({"error": str(e)}), 500

#     return app

# # Khởi tạo instance app cho Gunicorn/Docker
# app = create_app()

# if __name__ == "__main__":
#     # Debug mode chỉ dùng cho môi trường local
#     app.run(host="0.0.0.0", port=5000, debug=True)

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
    
    init_db(app)
    
    with app.app_context():
        try:
            from models.user import User, Feedback 
            db.create_all()
            # Kiểm tra và thêm cột is_read nếu chưa tồn tại (Dành cho MySQL)
            try:
                from sqlalchemy import text
                db.session.execute(text("ALTER TABLE feedbacks ADD COLUMN is_read BOOLEAN DEFAULT FALSE"))
                db.session.commit()
            except Exception:
                db.session.rollback() # Cột đã tồn tại, bỏ qua lỗi

            print(">>> [MySQL] Database đã sẵn sàng!")
        except Exception as e:
            print(f">>> [MySQL] Lỗi khởi tạo: {e}")
    
    CORS(app, resources={r"/*": {"origins": "*"}})
    jwt = JWTManager(app)

    # ĐĂNG KÝ BLUEPRINT
    app.register_blueprint(auth_bp, url_prefix='/auth') 
    app.register_blueprint(user_bp, url_prefix='/profile')
    app.register_blueprint(internal_bp, url_prefix='/internal')

    @app.get("/health")
    def health():
        return jsonify({"status": "ok", "service": "user-service"}), 200

    # 1. ROUTE: Lấy danh sách user cho Dashboard
    @app.get("/all")
    def get_all_users_direct():
        try:
            from sqlalchemy import text
            sql = text("SELECT id, username, email, role, status FROM users ORDER BY id DESC")
            result = db.session.execute(sql)
            users = [dict(r._mapping) for r in result]
            return jsonify(users), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    # 2. API: Lấy danh sách phản hồi (Bổ sung id và is_read)
    @app.get("/feedbacks/all")
    def get_all_feedbacks():
        try:
            from models.user import Feedback, User
            # Join lấy dữ liệu bao gồm trạng thái is_read
            feedbacks = db.session.query(
                Feedback.id,
                Feedback.content, 
                Feedback.rating, 
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
                    "target": fb.target_name,
                    "content": fb.content,
                    "rating": fb.rating,
                    "date": fb.created_at.strftime("%d/%m/%Y"),
                    "is_read": fb.is_read if fb.is_read is not None else False
                })
            return jsonify(result), 200
        except Exception as e:
            print(f"Lỗi lấy feedbacks: {e}")
            return jsonify({"error": str(e)}), 500

    # 3. API: Đánh dấu đã đọc (Lưu trạng thái tối xuống)
    @app.put("/feedbacks/<int:fb_id>/read")
    def mark_feedback_read(fb_id):
        try:
            from models.user import Feedback
            fb = Feedback.query.get(fb_id)
            if not fb:
                return jsonify({"error": "Không tìm thấy"}), 404
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
            fb = Feedback.query.get(fb_id)
            if not fb:
                return jsonify({"error": "Không tìm thấy"}), 404
            db.session.delete(fb)
            db.session.commit()
            return jsonify({"success": True}), 200
        except Exception as e:
            db.session.rollback()
            return jsonify({"error": str(e)}), 500

    # 5. API: Gửi phản hồi ngược lại cho User
    @app.post("/feedbacks/reply")
    def reply_feedback():
        try:
            data = request.json
            email = data.get('email')
            message = data.get('message')
            print(f">>> [REPLY] Gửi tới {email}: {message}")
            return jsonify({"success": True, "message": f"Đã gửi trả lời tới {email}"}), 200
        except Exception as e:
            return jsonify({"error": str(e)}), 500

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5000, debug=True)