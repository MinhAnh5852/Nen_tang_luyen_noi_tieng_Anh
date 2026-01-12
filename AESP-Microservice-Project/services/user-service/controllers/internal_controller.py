from flask import Blueprint, request, jsonify, current_app
import jwt

internal_bp = Blueprint("internal", __name__)

@internal_bp.route("/internal/verify", methods=["GET"])
def verify():
    auth = request.headers.get("Authorization", "")
    if not auth.startswith("Bearer "):
        return jsonify({"valid": False, "error": "Missing Bearer token"}), 401

    token = auth.split(" ", 1)[1].strip()
    secret = current_app.config.get("JWT_SECRET_KEY")

    if not secret:
        return jsonify({"valid": False, "error": "Server missing JWT secret"}), 500

    try:
        payload = jwt.decode(token, secret, algorithms=["HS256"])

        user_id = payload.get("user_id")
        role = payload.get("role")

        # role có thể đang là enum hoặc string
        role_str = getattr(role, "value", None) or (str(role) if role is not None else None)

        # Nếu trước đây role bị dạng "UserRole.LEARNER" thì normalize về "learner"
        if isinstance(role_str, str) and "." in role_str:
            role_str = role_str.split(".", 1)[1].lower()
        elif isinstance(role_str, str):
            role_str = role_str.lower()

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
        return jsonify({"valid": False, "error": "Internal error", "detail": str(e)}), 500
