from flask import Blueprint, request, jsonify
from services.payment_service import PaymentService
from sqlalchemy import text
from database import db
import requests
import traceback

# Blueprint có url_prefix='/api/payments'
payment_bp = Blueprint('payment_bp', __name__, url_prefix='/api/payments')

@payment_bp.route("/create", methods=["POST"])
def create_payment():
    """Tạo giao dịch thanh toán mới"""
    data = request.json
    user_id = data.get('user_id')
    package_id = data.get('package_id')
    package_name = data.get('package_name')
    method = data.get('method', 'qr_code')
    
    if not all([user_id, package_id, package_name]):
        return jsonify({"error": "Thiếu thông tin user_id, package_id hoặc package_name"}), 400

    try:
        # Lấy giá gói từ database subscription_db
        sql = text("SELECT price FROM subscription_db.subscription_plans WHERE id = :p_id AND is_active = 1")
        result = db.session.execute(sql, {"p_id": package_id}).fetchone()
        
        if not result:
            return jsonify({"error": f"Gói ID '{package_id}' không tồn tại hoặc đã bị đóng"}), 400
        
        amount = result[0] 
        if amount <= 0:
            return jsonify({"error": "Gói này mặc định miễn phí, không cần tạo giao dịch"}), 400

        # Tạo giao dịch qua Service
        new_tx = PaymentService.create_payment(
            user_id=user_id,
            amount=amount,
            method=method,
            package_id=package_id,
            package_name=package_name
        )

        response_data = {
            "transaction_id": new_tx.id,
            "status": new_tx.status,
            "amount": new_tx.amount,
            "package_id": new_tx.package_id,
            "package_name": new_tx.package_name
        }

        if method == 'qr_code':
            qr_url = f"https://img.vietqr.io/image/MB-123456789-compact2.jpg?amount={int(amount)}&addInfo=AESP_PAY_{new_tx.id}"
            response_data["qr_url"] = qr_url
        else:
            response_data["message"] = "Vui lòng thanh toán tiền mặt tại quầy"
            
        return jsonify(response_data), 201
        
    except Exception as e:
        print(traceback.format_exc())
        return jsonify({"error": f"Lỗi hệ thống: {str(e)}"}), 500

@payment_bp.route("/confirm/<int:tx_id>", methods=["POST"])
def confirm_payment(tx_id):
    """Xác nhận thanh toán (Admin duyệt)"""
    try:
        payment, message = PaymentService.update_payment_status(
            payment_id=tx_id, 
            status="SUCCESS"
        )

        if message == "UPDATED":
            # GỌI SANG USER SERVICE ĐỂ NÂNG CẤP GÓI (Sửa path nội bộ cho chuẩn)
            try:
                requests.post("http://user-service:5000/api/users/internal/upgrade-package", json={
                    "user_id": payment.user_id,
                    "package_name": payment.package_name
                }, timeout=5)
            except Exception as e:
                print(f"⚠️ Cảnh báo: Giao dịch OK nhưng chưa gọi được User Service: {e}")

            return jsonify({
                "message": f"Thành công! Đã duyệt đơn #INV-{tx_id}",
                "status": payment.status
            }), 200
        
        return jsonify({"error": "Không thể cập nhật trạng thái đơn hàng"}), 400
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@payment_bp.route("/all", methods=["GET"])
def get_all_payments():
    """Lấy toàn bộ lịch sử cho Admin"""
    try:
        from models.transaction import Transaction
        transactions = Transaction.query.order_by(Transaction.created_at.desc()).all()
        
        result = []
        for tx in transactions:
            data = tx.to_dict()
            # 🔥 Fix mapping cho HTML: Gán payment_method vào key 'method'
            data['method'] = tx.payment_method
            # Format lại thời gian cho JS dễ hiển thị
            if data['created_at']:
                data['created_at'] = tx.created_at.strftime('%Y-%m-%d %H:%M:%S')
            result.append(data)
            
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@payment_bp.route("/history/<string:user_id>", methods=["GET"])
def get_payment_history(user_id):
    """Lấy lịch sử cho 1 User cụ thể"""
    try:
        from models.transaction import Transaction
        transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.created_at.desc()).all()
        
        result = []
        for tx in transactions:
            data = tx.to_dict()
            data['method'] = tx.payment_method
            if data['created_at']:
                data['created_at'] = tx.created_at.strftime('%Y-%m-%d %H:%M:%S')
            result.append(data)
            
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500