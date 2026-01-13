from models.subscription import Subscription
from database import db
from datetime import datetime

def _parse_iso_datetime(value: str) -> datetime:
    if not isinstance(value, str) or not value.strip():
        raise ValueError("Invalid datetime string")
    s = value.strip()
    if s.endswith("Z"):
        s = s[:-1]
    return datetime.fromisoformat(s)

class SubscriptionService:
    @staticmethod
    def create_subscription(user_id, package_id, start_date, end_date):
        start_dt = _parse_iso_datetime(start_date) if isinstance(start_date, str) else start_date
        end_dt = _parse_iso_datetime(end_date) if isinstance(end_date, str) else end_date

        subscription = Subscription(
            user_id=user_id,
            package_id=package_id,
            start_date=start_dt,
            end_date=end_dt,
            status="ACTIVE"
        )
        db.session.add(subscription)
        db.session.commit()
        return subscription

    @staticmethod
    def cancel_subscription(subscription_id: str):
        subscription = Subscription.query.get(subscription_id)
        if not subscription:
            return None
        subscription.status = "CANCELLED"
        db.session.commit()
        return subscription

    @staticmethod
    def get_subscription_by_user(user_id: str):
        return Subscription.query.filter_by(user_id=user_id).first()

    @staticmethod
    def activate_subscription(subscription_id: str):
        """
        Option A: chỉ activate subscription đã tồn tại (không tạo mới)
        """
        subscription = Subscription.query.get(subscription_id)
        if not subscription:
            return None
        if subscription.end_date < datetime.utcnow():
            raise ValueError("Subscription expired")
        subscription.status = "ACTIVE"
        db.session.commit()
        return subscription
