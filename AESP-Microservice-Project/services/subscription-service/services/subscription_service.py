from models.subscription import SubscriptionPlan
from database import db

class SubscriptionService:
    @staticmethod
    def get_subscription_by_user(user_id):
        """
        Logic kiểm tra gói của User. 
        Hiện tại bạn mới có bảng subscription_plans (danh sách gói), 
        chưa có bảng UserSubscriptions (người dùng nào mua gói nào).
        Tạm thời trả về None để hệ thống không crash.
        """
        try:
            # Sau này Trọng sẽ code thêm bảng UserSubscriptions ở đây
            return None 
        except Exception as e:
            return None