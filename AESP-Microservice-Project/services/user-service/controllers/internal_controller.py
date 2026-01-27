from flask import Blueprint, request, jsonify, current_app
import jwt
from models.user import User 

internal_bp = Blueprint("internal", __name__)

@internal_bp.route("/verify", methods=["GET"])
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
        # LƯU Ý: Flask-JWT-Extended mặc định dùng 'sub' làm identity (user_id)
        payload = jwt.decode(token, secret, algorithms=["HS256"])

        # Kiểm tra cả hai trường hợp 'sub' (từ Firebase sync) và 'user_id' (từ Auth truyền thống)
        user_id = payload.get("sub") or payload.get("user_id")
        role_from_token = payload.get("role")

        if not user_id:
            return jsonify({"valid": False, "error": "Token missing identity (sub/user_id)"}), 401

        # 2. Chuẩn hóa Role (Normalize)
        role_str = str(role_from_token).lower() if role_from_token else "learner"
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
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 401
        
    token = auth.split(" ", 1)[1].strip()
    secret = current_app.config.get("JWT_SECRET_KEY")
    
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        # Đồng bộ khóa 'role'
        user_role = str(payload.get("role", "")).lower()
        
        if user_role not in ["mentor", "admin"]:
            return jsonify({"error": "Unauthorized"}), 403
            
        # Truy vấn danh sách learner từ database
        learners = User.query.filter_by(role="learner").all()
        
        result = [{
            "id": u.id, 
            "email": u.email, 
            "username": u.username or u.email.split('@')[0],
            "status": str(u.status).lower() if u.status else "active"
        } for u in learners]
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": f"Invalid token or session: {str(e)}"}), 401