from flask import Blueprint, request, jsonify
from werkzeug.security import generate_password_hash
from database import db
from services.user_service import AuthService
from models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/register", methods=["POST"])
def register():
    data = request.get_json() or {}
    username = data.get("username")
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    role = (data.get("role") or "learner").lower()

    if not email or not password:
        return jsonify({"message": "Thiếu email hoặc mật khẩu"}), 400

    if User.query.filter_by(email=email).first():
        return jsonify({"message": "Email đã tồn tại"}), 409

    try:
        new_user = User(
            username=username,
            email=email,
            password=generate_password_hash(password),
            role=role
        )
        db.session.add(new_user)
        db.session.commit()
        return jsonify({"message": "Đăng ký thành công"}), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"message": str(e)}), 500

@auth_bp.route("/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    try:
        # Gọi AuthService để xác thực và lấy token
        token = AuthService().login(email, password)
        user = User.query.filter_by(email=email).first()
        
        # Chuyển role sang string để Frontend dễ xử lý
        role_str = user.role_str

        return jsonify({
            "token": token,
            "user": {
                "id": user.id,
                "username": user.username,
                "role": role_str
            }
        }), 200
    except Exception as e:
        return jsonify({"error": "Sai thông tin đăng nhập"}), 401