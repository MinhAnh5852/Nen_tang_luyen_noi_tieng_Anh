from flask import Blueprint, request, jsonify
from services.subscription_service import SubscriptionService

subscription_bp = Blueprint("subscription", __name__)

@subscription_bp.route("/status", methods=["GET"])
def get_subscription_status():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"message": "Missing user_id"}), 400

    # Lấy gói ACTIVE mới nhất từ service đã sửa ở trên
    subscription = SubscriptionService.get_subscription_by_user(user_id)
    
    if not subscription:
        return jsonify({
            "status": "inactive",
            "package_name": "Gói Miễn phí",
            "end_date": None
        }), 200

    # Ánh xạ tên hiển thị
    package_names = {
        "BASIC_MONTHLY": "Gói Cơ bản",
        "PREMIUM_MONTHLY": "Gói Premium"
    }

    return jsonify({
        "status": "active",
        "package_name": package_names.get(subscription.package_id, subscription.package_id),
        "end_date": subscription.end_date.isoformat()
    }), 200
# Các route khác giữ nguyên nhưng bỏ tiền tố /subscriptions nếu Nginx đã cấu hình
@subscription_bp.route("/", methods=["POST"])
def create_subscription():
    data = request.get_json(force=True) or {}
    required = ["user_id", "package_id", "start_date", "end_date"]
    if not all(data.get(k) for k in required):
        return jsonify({"message": "Missing fields"}), 400

    subscription = SubscriptionService.create_subscription(
        user_id=data["user_id"],
        package_id=data["package_id"],
        start_date=data["start_date"],
        end_date=data["end_date"]
    )
    return jsonify({"id": subscription.id, "status": subscription.status}), 201