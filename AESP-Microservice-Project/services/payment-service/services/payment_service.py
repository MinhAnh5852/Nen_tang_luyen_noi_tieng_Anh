import os
import requests
from models.transaction import Transaction as Payment 
from database import db
from datetime import datetime
from config import Config

# Cấu hình kiểm soát chuyển đổi trạng thái nghiêm ngặt
STRICT_PAYMENT_TRANSITIONS = os.getenv("STRICT_PAYMENT_TRANSITIONS", "true").lower() == "true"

class PaymentService:
    @staticmethod
    def create_payment(user_id, amount, method, package_name=None, currency="VND"):
        """Khởi tạo giao dịch mới vào payment_db"""
        payment = Payment(
            user_id=user_id,
            package_name=package_name,
            amount=int(amount),
            payment_method=method,
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
        """Kiểm tra trạng thái cuối (SUCCESS/FAILED)"""
        return status in ["SUCCESS", "FAILED"]

    @staticmethod
    def update_payment_status(*, payment_id=None, provider_txn_id=None, status=None):
        """
        Quy tắc: PENDING -> SUCCESS/FAILED.
        Khi SUCCESS: Tự động gọi User Service nâng cấp gói.
        """
        if status not in ["SUCCESS", "FAILED"]:
            raise ValueError("Trạng thái cập nhật không hợp lệ")

        payment = None
        if payment_id:
            payment = Payment.query.get(payment_id)
        elif provider_txn_id:
            payment = Payment.query.filter_by(provider_txn_id=provider_txn_id).first()

        if not payment:
            return None, "NOT_FOUND"

        # Chặn nếu giao dịch đã hoàn tất (Bảo mật thanh toán)
        if STRICT_PAYMENT_TRANSITIONS and PaymentService._is_terminal(payment.status):
            return payment, "TERMINAL_LOCKED"

        payment.status = status
        
        # Nếu SUCCESS, cập nhật thời gian thanh toán thực tế và gọi User Service
        if status == "SUCCESS":
            payment.paid_at = datetime.utcnow() # Cập nhật thời điểm nhận tiền
            
            try:
                # Gọi sang User Service để đồng bộ quyền lợi user
                response = requests.put(
                    Config.USER_SERVICE_INTERNAL_URL, 
                    json={
                        "user_id": payment.user_id,
                        "package_name": payment.package_name
                    },
                    timeout=5
                )
                
                if response.status_code != 200:
                    print(f">>> [Lỗi Nâng Cấp] User Service trả về lỗi cho User {payment.user_id}")
                else:
                    print(f">>> [Thành Công] Đã nâng cấp gói {payment.package_name} cho User {payment.user_id}")
            except Exception as e:
                print(f">>> [Lỗi Kết Nối] Không thể gọi User Service: {e}")

        db.session.commit()
        return payment, "UPDATED"

    @staticmethod
    def attach_provider_txn(*, payment_id, provider_txn_id):
        """Lưu mã đối soát ngân hàng (Cần thiết cho NiFi đối soát sau này)"""
        payment = Payment.query.get(payment_id)
        if not payment:
            return None
        payment.provider_txn_id = provider_txn_id 
        db.session.commit()
        return payment