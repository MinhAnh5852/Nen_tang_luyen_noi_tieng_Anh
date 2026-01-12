from flask import Blueprint, request, jsonify
from flask_limiter import Limiter

from services.user_service import AuthService
from models.user import User

auth_bp = Blueprint("auth", __name__)

@auth_bp.route("/auth/login", methods=["POST"])
def login():
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")

    if not email:
        return jsonify({"error": "Missing field: email"}), 400
    if not password:
        return jsonify({"error": "Missing field: password"}), 400

    try:
        # AuthService login: validate credentials + issue JWT
        token = AuthService().login(email, password)

        # Query user to return user_id + role (string)
        user = User.query.filter_by(email=email).first()

        # An toàn: user vẫn có thể None nếu DB lỗi, nhưng hiếm
        user_id = getattr(user, "id", None)
        role_obj = getattr(user, "role", None)
        role_str = getattr(role_obj, "value", None) or (str(role_obj) if role_obj is not None else None)

        return jsonify({
            "token": token,
            "user_id": user_id,
            "role": role_str
        }), 200

    except Exception:
        return jsonify({"error": "Invalid credentials"}), 401
