from flask import Blueprint, request, jsonify
from services.payment_service import PaymentService

payment_bp = Blueprint("payment", __name__)

@payment_bp.route("/payments", methods=["POST"])
def create_payment():
    data = request.get_json(force=True) or {}

    required = ["user_id", "amount", "method"]
    missing = [k for k in required if data.get(k) in [None, ""]]
    if missing:
        return jsonify({"message": f"Missing fields: {', '.join(missing)}"}), 400

    payment = PaymentService.create_payment(
        user_id=data["user_id"],
        amount=data["amount"],
        method=data["method"],
        subscription_id=data.get("subscription_id"),
        currency=data.get("currency", "VND")
    )

    return jsonify({
        "id": payment.id,
        "status": payment.status
    }), 201
