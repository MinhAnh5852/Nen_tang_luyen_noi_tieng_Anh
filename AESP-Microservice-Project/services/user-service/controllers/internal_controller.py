from flask import Blueprint, request, jsonify, current_app
import jwt
from models.user import User 
from database import db

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
        payload = jwt.decode(token, secret, algorithms=["HS256"])

        # Lấy identity từ token
        user_id = payload.get("user_id") or payload.get("sub")
        if not user_id:
            return jsonify({"valid": False, "error": "Token missing identity"}), 401

        # 2. Truy vấn DB để lấy thông tin mới nhất (Role, Package)
        user = User.query.get(user_id)
        if not user:
            return jsonify({"valid": False, "error": "User not found"}), 404

        # 3. Chuẩn hóa dữ liệu trả về
        role_str = user.role.value if hasattr(user.role, 'value') else str(user.role)
        role_str = role_str.lower()

        return jsonify({
            "valid": True,
            "user_id": user_id,
            "role": role_str,
            "package_id": user.package_id,     # Trả về để React nhận diện gói
            "package_name": user.package_name, # Trả về để hiện tên gói
            "status": user.status.value if hasattr(user.status, 'value') else str(user.status)
        }), 200

    except jwt.ExpiredSignatureError:
        return jsonify({"valid": False, "error": "Token expired"}), 401
    except jwt.InvalidTokenError:
        return jsonify({"valid": False, "error": "Invalid token"}), 401
    except Exception as e:
        return jsonify({"valid": False, "error": str(e)}), 500

# --- PHẦN BỔ SUNG: API NÂNG CẤP GÓI DỊCH VỤ ---
@internal_bp.route("/upgrade-package", methods=["PUT"])
def upgrade_package():
    """API nội bộ để Payment Service gọi sang sau khi thanh toán SUCCESS"""
    data = request.get_json()
    user_id = data.get("user_id")
    new_package_id = data.get("package_id")
    new_package_name = data.get("package_name")

    if not all([user_id, new_package_id, new_package_name]):
        return jsonify({"error": "Thiếu dữ liệu nâng cấp"}), 400

    user = User.query.get(user_id)
    if not user:
        return jsonify({"error": "Không tìm thấy người dùng"}), 404

    try:
        # Cập nhật thông tin gói mới vào DB của user_service
        user.package_id = new_package_id
        user.package_name = new_package_name
        
        db.session.commit()
        return jsonify({
            "message": "Nâng cấp gói thành công",
            "user_id": user_id,
            "new_package": new_package_name
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": f"Lỗi database: {str(e)}"}), 500

@internal_bp.route("/learners", methods=["GET"])
def get_learners():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"error": "Missing token"}), 401
        
    token = auth.split(" ", 1)[1].strip()
    secret = current_app.config.get("JWT_SECRET_KEY")
    
    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])
        user_role = str(payload.get("role", "")).lower()
        
        if "mentor" not in user_role and "admin" not in user_role:
            return jsonify({"error": "Unauthorized"}), 403
            
        learners = User.query.filter(User.role.ilike('%learner%')).all()
        
        result = [{
            "id": u.id, 
            "email": u.email, 
            "username": u.username or u.email.split('@')[0],
            "package_id": u.package_id,
            "package_name": u.package_name,
            "status": u.status.value if hasattr(u.status, 'value') else str(u.status)
        } for u in learners]
        
        return jsonify(result), 200
        
    except Exception as e:
        return jsonify({"error": f"Invalid session: {str(e)}"}), 401