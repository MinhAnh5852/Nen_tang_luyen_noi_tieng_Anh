from flask import Blueprint, request, jsonify
from sqlalchemy.exc import IntegrityError
from werkzeug.security import generate_password_hash

from database import db
from models.user import User
from models.enums import UserRole

user_bp = Blueprint("users", __name__)

@user_bp.route("/users/register", methods=["POST"])
def register():
    # Content-Type check
    if not request.is_json:
        return jsonify({"error": "Content-Type must be application/json"}), 415

    data = request.get_json(silent=True) or {}
    email = (data.get("email") or "").strip().lower()
    password = data.get("password")
    role_raw = (data.get("role") or "learner").strip().lower()

    # Validate required fields
    if not email:
        return jsonify({"error": "Missing field: email"}), 400
    if not password:
        return jsonify({"error": "Missing field: password"}), 400

    # Validate role
    try:
        role = UserRole(role_raw)
    except Exception:
        return jsonify({
            "error": "Invalid role",
            "allowed_roles": [r.value for r in UserRole]
        }), 400

    # Check duplicate email early (nice error message)
    existed = User.query.filter_by(email=email).first()
    if existed:
        return jsonify({"error": "Email already exists"}), 409

    try:
        u = User(
            email=email,
            password=generate_password_hash(password),
            role=role
        )
        db.session.add(u)
        db.session.commit()
        return jsonify({"id": u.id}), 201

    except IntegrityError:
        db.session.rollback()
        # In case race condition / unique constraint
        return jsonify({"error": "Email already exists"}), 409

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": "Internal Server Error", "detail": str(e)}), 500
