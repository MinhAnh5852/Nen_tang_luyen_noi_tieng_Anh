from flask import Blueprint, jsonify
from services.subscription_service import SubscriptionService

internal_bp = Blueprint("internal", __name__)

@internal_bp.route("/internal/subscription/<string:user_id>", methods=["GET"])
def check_subscription(user_id):
    subscription = SubscriptionService.get_subscription_by_user(user_id)

    if not subscription or subscription.status != "ACTIVE":
        return jsonify({"valid": False})

    return jsonify({
        "valid": True,
        "subscription_id": subscription.id,
        "status": subscription.status,
        "end_date": subscription.end_date.isoformat()
    })

@internal_bp.route("/internal/subscription/<string:subscription_id>/activate", methods=["PUT"])
def activate_subscription(subscription_id):
    sub = SubscriptionService.activate_subscription(subscription_id)
    if not sub:
        return jsonify({"message": "Subscription not found"}), 404

    return jsonify({
        "message": "Subscription activated",
        "subscription_id": sub.id,
        "status": sub.status
    })
