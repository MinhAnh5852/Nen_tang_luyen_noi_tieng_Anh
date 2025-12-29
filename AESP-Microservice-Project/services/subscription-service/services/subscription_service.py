from models.subscription import Subscription
from database import db
from datetime import datetime

class SubscriptionService:
    """
    Service xử lý nghiệp vụ Subscription
    """

    @staticmethod
    def create_subscription(user_id, package_id, start_date, end_date):
        subscription = Subscription(
            user_id=user_id,
            package_id=package_id,
            start_date=start_date,
            end_date=end_date,
            status="ACTIVE",
            created_at=datetime.utcnow()
        )
        db.session.add(subscription)
        db.session.commit()
        return subscription

    @staticmethod
    def cancel_subscription(subscription_id):
        subscription = Subscription.query.get(subscription_id)
        if not subscription:
            return None

        subscription.status = "CANCELLED"
        db.session.commit()
        return subscription

    @staticmethod
    def get_subscription_by_user(user_id):
        return Subscription.query.filter_by(user_id=user_id).first()
