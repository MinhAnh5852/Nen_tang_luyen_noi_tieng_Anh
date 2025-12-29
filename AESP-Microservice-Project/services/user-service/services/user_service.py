
from models.user import User
from models.enums import AccountStatus
from werkzeug.security import check_password_hash
import jwt,datetime
from config import Config

class AuthService:
    def login(self,email,password):
        user=User.query.filter_by(email=email).first()
        if not user or user.status==AccountStatus.DISABLED:
            raise Exception("Invalid user")
        if not check_password_hash(user.password,password):
            raise Exception("Invalid password")
        payload={"user_id":user.id,"exp":datetime.datetime.utcnow()+datetime.timedelta(hours=2)}
        return jwt.encode(payload,Config.JWT_SECRET_KEY,algorithm="HS256")
