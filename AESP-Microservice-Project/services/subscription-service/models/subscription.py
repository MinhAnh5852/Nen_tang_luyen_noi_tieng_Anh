from database import db
import uuid

class SubscriptionPlan(db.Model):
    __tablename__ = 'subscription_plans'
    
    # Dùng String(36) cho UUID là chuẩn bài
    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(100), nullable=False)
    price = db.Column(db.Float, nullable=False, default=0.0)
    duration_days = db.Column(db.Integer, default=30)
    badge_text = db.Column(db.String(50))
    features = db.Column(db.Text) # Lưu dạng chuỗi "Feature 1, Feature 2"
    is_active = db.Column(db.Boolean, default=True)

    def to_dict(self):
        # Đảm bảo xử lý trường hợp features bị None/Empty một cách an toàn
        features_list = []
        if self.features:
            # Tách chuỗi và xóa khoảng trắng thừa của từng phần tử
            features_list = [f.strip() for f in self.features.split(',') if f.strip()]

        return {
            "id": self.id,
            "name": self.name,
            "price": self.price,
            "duration_days": self.duration_days,
            "badge_text": self.badge_text or "",
            "features": features_list,
            "is_active": self.is_active
        }