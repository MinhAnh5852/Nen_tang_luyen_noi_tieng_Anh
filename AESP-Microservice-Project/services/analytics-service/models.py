from database import db
from datetime import datetime

class SystemStat(db.Model):
    __tablename__ = 'system_stats'
    
    # Key định danh: 'total_users', 'total_revenue', 'active_mentors'
    key = db.Column(db.String(50), primary_key=True) 
    
    # SỬA: Dùng Float để lưu được số tiền doanh thu lớn (VND) 
    # Nếu dùng Integer sẽ bị giới hạn con số khoảng 2 tỷ, không đủ cho doanh thu lâu dài
    value = db.Column(db.Float, default=0.0)

    def to_dict(self):
        return {
            "key": self.key,
            "value": self.value
        }

class ActivityLog(db.Model):
    __tablename__ = 'activity_logs'
    
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    message = db.Column(db.String(255), nullable=False)
    
    # Thời điểm ghi log
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    def to_dict(self):
        return {
            "id": self.id,
            "message": self.message,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S")
        }