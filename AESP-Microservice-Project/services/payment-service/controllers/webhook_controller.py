from flask import Blueprint, request, jsonify
from services.payment_service import PaymentService
import os
import requests

webhook_bp = Blueprint("webhook", __name__)

SUBSCRIPTION_SERVICE_URL = os.getenv("SUBSCRIPTION_SERVICE_URL", "http://subscription-service:5001")
ACTIVATE_ON_SUCCESS = os.getenv("PAYMENT_ACTIVATES_SUBSCRIPTION", "true").lower() == "true"

@webhook_bp.route("/webhook/payment", methods=["POST"])
def handle_payment_webhook():
    """
    Webhook UPDATE payment (không tạo mới).
    Payload tối thiểu:
      - payment_id hoặc provider_txn_id
      - status: SUCCESS | FAILED
      - provider_txn_id (optional)
    Option A: nếu SUCCESS và payment có subscription_id -> gọi subscription-service activate subscription đó.
    """
    data = request.get_json(force=True) or {}

    status = data.get("status")
    payment_id = data.get("payment_id")
    provider_txn_id = data.get("provider_txn_id")

    if not status or status not in ["SUCCESS", "FAILED"]:
        return jsonify({"message": "Invalid or missing status"}), 400

    if not payment_id and not provider_txn_id:
        return jsonify({"message": "Missing payment_id or provider_txn_id"}), 400

    payment, result = PaymentService.update_payment_status(
        payment_id=payment_id,
        provider_txn_id=provider_txn_id,
        status=status
    )

    if result == "NOT_FOUND":
        return jsonify({"message": "Payment not found"}), 404

    if result == "TERMINAL_LOCKED":
        # Đã SUCCESS/FAILED rồi thì không cho đổi nữa
        return jsonify({
            "message": f"Payment already {payment.status}. Status change is not allowed.",
            "id": payment.id,
            "status": payment.status
        }), 409

    # Nếu có provider_txn_id thì gắn vào payment (tuỳ payload gửi lên)
    if provider_txn_id and not getattr(payment, "provider_txn_id", None):
        PaymentService.attach_provider_txn(payment_id=payment.id, provider_txn_id=provider_txn_id)

    activation = None

    # Option A: SUCCESS -> activate subscription đã có sẵn subscription_id
    if ACTIVATE_ON_SUCCESS and status == "SUCCESS":
        sub_id = getattr(payment, "subscription_id", None)
        if sub_id:
            try:
                r = requests.put(
                    f"{SUBSCRIPTION_SERVICE_URL}/internal/subscription/{sub_id}/activate",
                    timeout=3
                )
                if r.status_code == 200:
                    activation = "activated"
                elif r.status_code == 404:
                    activation = "subscription_not_found"
                else:
                    activation = f"activate_failed_{r.status_code}"
            except Exception:
                activation = "activate_failed_timeout_or_network"

    resp = {
        "message": "Payment updated",
        "id": payment.id,
        "status": payment.status
    }
    # Thêm field này không phá API cũ, chỉ bổ sung info
    if activation is not None:
        resp["subscription_activation"] = activation

    return jsonify(resp)
