from flask import Blueprint, jsonify
from services.subscription_service import SubscriptionService

internal_bp = Blueprint("internal", __name__)

@internal_bp.route("/internal/subscription/<int:user_id>", methods=["GET"])
def check_subscription(user_id):
    subscription = SubscriptionService.get_subscription_by_user(user_id)

    if not subscription or subscription.status != "ACTIVE":
        return jsonify({"valid": False})

    return jsonify({"valid": True})
