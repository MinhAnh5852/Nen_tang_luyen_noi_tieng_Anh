from models.payment import Payment
from database import db
from datetime import datetime
import os

STRICT_PAYMENT_TRANSITIONS = os.getenv("STRICT_PAYMENT_TRANSITIONS", "true").lower() == "true"

class PaymentService:
    @staticmethod
    def create_payment(user_id, amount, method, subscription_id=None, currency="VND"):
        payment = Payment(
            user_id=user_id,
            subscription_id=subscription_id,
            amount=int(amount),
            currency=currency,
            method=method,
            status="PENDING",
            created_at=datetime.utcnow()
        )
        db.session.add(payment)
        db.session.commit()
        return payment

    @staticmethod
    def get_payment(payment_id):
        return Payment.query.get(payment_id)

    @staticmethod
    def _is_terminal(status: str) -> bool:
        return status in ["SUCCESS", "FAILED"]

    @staticmethod
    def update_payment_status(*, payment_id=None, provider_txn_id=None, status=None):
        """
        Rule (STRICT):
          PENDING -> SUCCESS/FAILED
          SUCCESS/FAILED -> không đổi nữa
        """
        if not status:
            raise ValueError("Missing status")

        if status not in ["SUCCESS", "FAILED"]:
            raise ValueError("Invalid status")

        payment = None
        if payment_id:
            payment = Payment.query.get(payment_id)
        elif provider_txn_id:
            payment = Payment.query.filter_by(provider_txn_id=provider_txn_id).first()

        if not payment:
            return None, "NOT_FOUND"

        # Chặn chuyển trạng thái sai
        if STRICT_PAYMENT_TRANSITIONS and PaymentService._is_terminal(payment.status):
            return payment, "TERMINAL_LOCKED"

        payment.status = status
        if status == "SUCCESS":
            payment.paid_at = datetime.utcnow()

        db.session.commit()
        return payment, "UPDATED"

    @staticmethod
    def attach_provider_txn(*, payment_id, provider_txn_id):
        payment = Payment.query.get(payment_id)
        if not payment:
            return None
        payment.provider_txn_id = provider_txn_id
        db.session.commit()
        return payment
