from models.payment import Payment
from database import db
from datetime import datetime

class PaymentService:
    """
    Service xử lý nghiệp vụ Payment
    """

    @staticmethod
    def create_payment(user_id, amount, method):
        payment = Payment(
            user_id=user_id,
            amount=amount,
            method=method,
            status="SUCCESS",
            created_at=datetime.utcnow()
        )
        db.session.add(payment)
        db.session.commit()
        return payment

    @staticmethod
    def get_payment(payment_id):
        return Payment.query.get(payment_id)
