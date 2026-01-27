from database import db
from datetime import datetime

class Transaction(db.Model):
    __tablename__ = 'transactions'

    id = db.Column(db.Integer, primary_key=True, autoincrement=True)
    
    # Khớp với định dạng UUID String(36) bên User Service
    user_id = db.Column(db.String(36), nullable=False) 
    
    amount = db.Column(db.Float, nullable=False)
    
    # Tên gói: Premium, VIP... dùng để nâng cấp tài khoản
    package_name = db.Column(db.String(50), nullable=False)
    
    # Phương thức: 'cash' hoặc 'qr_code'
    payment_method = db.Column(db.String(20), nullable=False) 
    
    # Trạng thái: 'PENDING', 'SUCCESS', 'FAILED'
    status = db.Column(db.String(20), default='PENDING') 
    
    # Mã giao dịch từ phía Ngân hàng (Dùng để NiFi đối soát)
    provider_txn_id = db.Column(db.String(100), nullable=True, unique=True)
    
    # Thời điểm giao dịch thành công
    paid_at = db.Column(db.DateTime, nullable=True)
    
    # Thời điểm tạo lệnh
    created_at = db.Column(db.DateTime, default=datetime.utcnow)

    # --- BỔ SUNG DÒNG NÀY ĐỂ HÀM TO_DICT KHÔNG BỊ LỖI ---
    updated_at = db.Column(db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)

    def to_dict(self):
        """Hàm hỗ trợ chuyển đổi sang JSON nhanh với kiểm tra giá trị NULL"""
        return {
            "id": self.id,
            "user_id": self.user_id,
            "amount": self.amount,
            "package_name": self.package_name,
            "method": self.payment_method,
            "status": self.status,
            "provider_txn_id": self.provider_txn_id,
            # Kiểm tra nếu có dữ liệu thì mới format, không thì trả về chuỗi rỗng hoặc None
            "created_at": self.created_at.strftime("%Y-%m-%d %H:%M:%S") if self.created_at else "",
            "updated_at": self.updated_at.strftime("%Y-%m-%d %H:%M:%S") if self.updated_at else "",
            "paid_at": self.paid_at.strftime("%Y-%m-%d %H:%M:%S") if self.paid_at else None
        }