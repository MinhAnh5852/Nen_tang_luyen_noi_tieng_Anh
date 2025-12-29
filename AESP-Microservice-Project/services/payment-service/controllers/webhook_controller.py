from flask import Blueprint, request, jsonify
from services.payment_service import PaymentService

webhook_bp = Blueprint("webhook", __name__)

@webhook_bp.route("/webhook/payment", methods=["POST"])
def handle_payment_webhook():
    data = request.json

    payment = PaymentService.create_payment(
        user_id=data["user_id"],
        amount=data["amount"],
        method=data["method"]
    )

    return jsonify({"message": "Payment recorded"})
