from flask import Blueprint, request, jsonify, current_app
import jwt
from models.user import User # Import ngay từ đầu để dùng

internal_bp = Blueprint("internal", __name__)

@internal_bp.route("/verify", methods=["GET"]) # Bỏ /internal vì Prefix đã có trong app.py
def verify():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"valid": False, "error": "Missing Bearer token"}), 401

    token = auth.split(" ", 1)[1].strip()
    secret = current_app.config.get("JWT_SECRET_KEY")

    if not secret:
        return jsonify({"valid": False, "error": "Server missing JWT secret"}), 500

    try:
        # 1. Giải mã Token
        payload = jwt.decode(token, secret, algorithms=["HS256"])

        user_id = payload.get("user_id")
        role_from_token = payload.get("role")

        # 2. Normalize Role (Đảm bảo trả về chuỗi thường: admin, learner, mentor)
        role_str = str(role_from_token).lower()
        if "." in role_str:
            role_str = role_str.split(".", 1)[1]

        return jsonify({
            "valid": True,
            "user_id": user_id,
            "role": role_str
        }), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"valid": False, "error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"valid": False, "error": "Invalid token"}), 401
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

@internal_bp.route("/learners", methods=["GET"])
def get_learners():
    # Kiểm tra quyền Mentor
    auth = request.headers.get("Authorization", "")
    token = auth.split(" ", 1)[1] if " " in auth else ""
    secret = current_app.config.get("JWT_SECRET_KEY")
    
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        # Kiểm tra role (phải trùng với Enum: learner, mentor, admin)
        if payload.get("role") not in ["mentor", "admin"]:
            return jsonify({"error": "Unauthorized"}), 403
    except:
        return jsonify({"error": "Invalid token"}), 401

    # Lấy danh sách học viên từ MySQL
    # Lưu ý: Role trong DB mình đang lưu là chữ thường 'learner'
    learners = User.query.filter_by(role="learner").all()
    
    result = [{
        "id": u.id, 
        "email": u.email, 
        "status": str(u.status) # Chuyển Enum status sang string
    } for u in learners]
    
    return jsonify(result), 200