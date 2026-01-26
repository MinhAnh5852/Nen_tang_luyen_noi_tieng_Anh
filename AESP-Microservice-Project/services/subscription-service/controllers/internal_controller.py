from flask import Blueprint, jsonify
# Chú ý: import từ đúng thư mục services bạn vừa chụp
from services.subscription_service import SubscriptionService
import logging

logger = logging.getLogger("InternalController")
internal_bp = Blueprint("internal", __name__)

@internal_bp.route("/internal/subscription/<string:user_id>", methods=["GET"])
def get_user_subscription(user_id):
    try:
        sub_info = SubscriptionService.get_subscription_by_user(user_id)
        
        if not sub_info:
            return jsonify({
                "has_subscription": False, 
                "message": "Người dùng chưa đăng ký gói"
            }), 200
            
        return jsonify({
            "has_subscription": True,
            "plan_name": sub_info.get('plan_name'),
            "status": "active"
        }), 200
        
    except Exception as e:
        logger.error(f"Lỗi: {str(e)}")
        return jsonify({"error": "Lỗi hệ thống nội bộ"}), 500