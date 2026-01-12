from datetime import datetime, timedelta, timezone

import jwt
from flask import current_app
from werkzeug.security import check_password_hash

from models.user import User


class AuthService:
    def login(self, email, password):
        user = User.query.filter_by(email=email).first()
        if not user:
            raise Exception("Invalid credentials")

        if not check_password_hash(user.password, password):
            raise Exception("Invalid credentials")

        secret = current_app.config.get("JWT_SECRET_KEY")
        if not secret:
            raise Exception("JWT secret not configured")

        exp = datetime.now(timezone.utc) + timedelta(hours=24)

        payload = {
            "user_id": user.id,
            # ✅ thêm role vào token (string)
            "role": getattr(user.role, "value", str(user.role)).lower(),
            "exp": exp,
        }

        token = jwt.encode(payload, secret, algorithm="HS256")
        return token
