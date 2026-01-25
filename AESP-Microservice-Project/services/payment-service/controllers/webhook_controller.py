from flask import Blueprint, request, jsonify
from services.payment_service import PaymentService
from datetime import datetime, timedelta
import os
import requests

webhook_bp = Blueprint("webhook", __name__)

SUBSCRIPTION_SERVICE_URL = os.getenv("SUBSCRIPTION_SERVICE_URL", "http://subscription-service:5001")
ACTIVATE_ON_SUCCESS = os.getenv("PAYMENT_ACTIVATES_SUBSCRIPTION", "true").lower() == "true"

@webhook_bp.route("/webhook/payment", methods=["POST"])
def handle_payment_webhook():
    data = request.get_json(force=True) or {}
    status = data.get("status")
    payment_id = data.get("payment_id")

    if not status or status not in ["SUCCESS", "FAILED"]:
        return jsonify({"message": "Invalid status"}), 400

    payment, result = PaymentService.update_payment_status(
        payment_id=payment_id,
        status=status
    )

    if result == "NOT_FOUND":
        return jsonify({"message": "Payment not found"}), 404

    activation = None

    # TỰ ĐỘNG TẠO GÓI CƯỚC KHI THANH TOÁN THÀNH CÔNG
    if ACTIVATE_ON_SUCCESS and status == "SUCCESS":
        # Thiết lập thời gian gói 30 ngày
        start_date = datetime.utcnow().isoformat()
        end_date = (datetime.utcnow() + timedelta(days=30)).isoformat()
        
        try:
            # Gọi API tạo mới Subscription bên subscription-service
            r = requests.post(
                f"{SUBSCRIPTION_SERVICE_URL}/", 
                json={
                    "user_id": payment.user_id,
                    "package_id": getattr(payment, "package_id", "BASIC_MONTHLY"),
                    "start_date": start_date,
                    "end_date": end_date
                },
                timeout=5
            )
            
            if r.status_code == 201:
                activation = "subscription_created_and_activated"
            else:
                activation = f"creation_failed_code_{r.status_code}"
        except Exception as e:
            activation = f"network_error_activating_sub: {str(e)}"

    resp = {
        "message": "Payment updated",
        "id": payment.id,
        "status": payment.status
    }
    if activation:
        resp["subscription_status"] = activation

    return jsonify(resp)