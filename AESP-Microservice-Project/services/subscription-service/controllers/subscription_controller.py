from flask import Blueprint, request, jsonify
from services.subscription_service import SubscriptionService

subscription_bp = Blueprint("subscription", __name__)

@subscription_bp.route("/subscriptions", methods=["POST"])
def create_subscription():
    data = request.get_json(force=True) or {}

    required = ["user_id", "package_id", "start_date", "end_date"]
    missing = [k for k in required if not data.get(k)]
    if missing:
        return jsonify({"message": f"Missing fields: {', '.join(missing)}"}), 400

    subscription = SubscriptionService.create_subscription(
        user_id=data["user_id"],
        package_id=data["package_id"],
        start_date=data["start_date"],
        end_date=data["end_date"]
    )

    return jsonify({
        "id": subscription.id,
        "status": subscription.status
    }), 201


@subscription_bp.route("/subscriptions/<string:id>/cancel", methods=["PUT"])
def cancel_subscription(id):
    subscription = SubscriptionService.cancel_subscription(id)

    if not subscription:
        return jsonify({"message": "Subscription not found"}), 404

    return jsonify({"status": subscription.status})
