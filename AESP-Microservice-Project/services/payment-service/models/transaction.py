from database import db
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = 'transactions'

    # Sử dụng Integer autoincrement để khớp với script SQL (DATABASE: payment_db)
    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Khớp với định dạng UUID String bên User Service
    user_id = db.Column(db.String(100), nullable=False, index=True) 
    
    amount = db.Column(db.Float, nullable=False)
    
    # --- QUAN TRỌNG: Đồng bộ với logic gói mới ---
    # Tên hiển thị: "Gói Pro AI", "Gói Cơ Bản"...
    package_name = db.Column(db.String(50), nullable=False)
    # ID logic để React so sánh: "pro-id-002", "plan-basic-001"...
    package_id = db.Column(db.String(50), nullable=False) 
    
    # Phương thức: 'cash', 'qr_code', 'VNPAY'
    payment_method = db.Column(db.String(20), nullable=False) 
    
    # Trạng thái: 'PENDING', 'SUCCESS', 'FAILED'
    status = db.Column(db.String(20), default='PENDING', index=True) 
    
    # Mã giao dịch từ phía Ngân hàng/Provider
    provider_txn_id = db.Column(db.String(100), nullable=True, unique=True)
    
    # Thời điểm giao dịch thành công
    paid_at = db.Column(db.DateTime, nullable=True)
    
    # Thời điểm tạo lệnh và cập nhật
    created_at = db.Column(db.DateTime, default=datetime.utcnow)
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Hàm hỗ trợ chuyển đổi sang JSON nhanh cho API"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "package_name": self.package_name,
            "package_id": self.package_id,  # Trả về để Frontend xử lý
            "method": self.payment_method,
            "status": self.status,
            "provider_txn_id": self.provider_txn_id,
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else "",
            "paid_at": self.paid_at.strftime("%Y-%m-%d %H:%M:%S") if self.paid_at else None
        }