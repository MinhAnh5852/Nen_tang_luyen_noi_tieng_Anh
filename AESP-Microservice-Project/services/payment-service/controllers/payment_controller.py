from flask import Blueprint, request, jsonify
from services.payment_service import PaymentService

payment_bp = Blueprint('payment_bp', __name__)

@payment_bp.route("/create", methods=["POST"])
def create_payment():
    data = request.json
    user_id = data.get('user_id')
    package = data.get('package_name')
    method = data.get('method')
    
    prices = {"Premium": 200000, "VIP": 500000}
    amount = prices.get(package, 0)

    try:
        new_tx = PaymentService.create_payment(
            user_id=user_id,
            amount=amount,
            method=method,
            package_name=package
        )

        response_data = {
            "transaction_id": new_tx.id,
            "status": new_tx.status, # Lấy trực tiếp từ Model
            "amount": new_tx.amount
        }

        if method == 'qr_code':
            qr_url = f"https://img.vietqr.io/image/MB-123456789-compact2.jpg?amount={amount}&addInfo=AESP_PAY_{new_tx.id}"
            response_data["qr_url"] = qr_url
            return jsonify(response_data), 201
        
        response_data["message"] = "Vui lòng thanh toán tiền mặt tại quầy"
        return jsonify(response_data), 201
        
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@payment_bp.route("/confirm/<int:tx_id>", methods=["POST"])
def confirm_payment(tx_id):
    payment, message = PaymentService.update_payment_status(
        payment_id=tx_id, 
        status="SUCCESS"
    )

    if message == "NOT_FOUND":
        return jsonify({"error": "Không tìm thấy giao dịch"}), 404
    
    if message == "TERMINAL_LOCKED":
        return jsonify({"error": "Giao dịch này đã hoàn tất trước đó"}), 400

    if message == "UPDATED":
        return jsonify({
            "message": f"Xác nhận thành công! Đã nâng cấp gói {payment.package_name}",
            "status": payment.status,
            "updated_at": payment.updated_at.strftime("%Y-%m-%d %H:%M:%S")
        }), 200
    
    return jsonify({"error": "Có lỗi xảy ra"}), 500

# --- NÊN THÊM: API lấy thông tin giao dịch để test hoặc dùng cho NiFi ---
@payment_bp.route("/<int:tx_id>", methods=["GET"])
def get_payment_detail(tx_id):
    payment = PaymentService.get_payment(tx_id)
    if not payment:
        return jsonify({"error": "Không tìm thấy"}), 404
    return jsonify(payment.to_dict()), 200

@payment_bp.route("/all", methods=["GET"])
def get_all_payments():
    # Import model trực tiếp bên trong hàm để tránh bị lỗi vòng lặp import (nếu có)
    from models.transaction import Transaction
    
    # Lấy tất cả giao dịch, cái nào mới nhất xếp lên đầu
    transactions = Transaction.query.order_by(Transaction.created_at.desc()).all()
    
    # Trả về danh sách dưới dạng JSON
    return jsonify([tx.to_dict() for tx in transactions]), 200