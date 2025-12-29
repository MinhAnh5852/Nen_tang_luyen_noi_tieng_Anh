from flask import Blueprint, request, jsonify
from services.payment_service import PaymentService

payment_bp = Blueprint("payment", __name__)

@payment_bp.route("/payments", methods=["POST"])
def create_payment():
    data = request.json

    payment = PaymentService.create_payment(
        user_id=data["user_id"],
        amount=data["amount"],
        method=data["method"]
    )

    return jsonify({
        "id": payment.id,
        "status": payment.status
    })
