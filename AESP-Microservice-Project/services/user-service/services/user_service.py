from datetime import datetime, timedelta, timezone
import jwt
from flask import current_app
from werkzeug.security import check_password_hash
from models.user import User

class AuthService:
    def login(self, email, password):
        # 1. Tìm user bằng Email trong MySQL
        user = User.query.filter_by(email=email).first()
        if not user:
            raise Exception("Email không tồn tại!")

        # 2. Kiểm tra mật khẩu (Sử dụng hash để bảo mật)
        if not check_password_hash(user.password, password):
            raise Exception("Mật khẩu không đúng!")

        # 3. Lấy Secret Key từ Config (đã nạp từ .env)
        secret = current_app.config.get("JWT_SECRET_KEY")
        if not secret:
            raise Exception("JWT secret chưa được cấu hình!")

        # 4. Thiết lập thời gian hết hạn (24 giờ)
        exp = datetime.now(timezone.utc) + timedelta(hours=24)

        # 5. Đóng gói Payload
        payload = {
            "user_id": user.id,
            "email": user.email,
            # ✅ SỬA: Trong MySQL mình dùng 'role', không phải 'role_str'
            "role": user.role, 
            "exp": exp,
        }

        # 6. Mã hóa JWT Token
        token = jwt.encode(payload, secret, algorithm="HS256")
        
        # Nên trả về cả thông tin user để Frontend hiển thị Dashboard
        return {
            "token": token,
            "user": {
                "email": user.email,
                "role": user.role
            }
        }