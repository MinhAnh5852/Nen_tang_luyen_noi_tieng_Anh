from flask import Blueprint, request, jsonify
from services.payment_service import PaymentService
from sqlalchemy import text
from database import db

payment_bp = Blueprint('payment_bp', __name__)

@payment_bp.route("/create", methods=["POST"])
def create_payment():
    """Tạo giao dịch thanh toán mới"""
    data = request.json
    user_id = data.get('user_id')
    package_id = data.get('package_id')     # Dùng để logic so sánh ở React
    package_name = data.get('package_name') # Dùng để hiển thị tên gói
    method = data.get('method')
    
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

    except Exception as e:
        return jsonify({"error": f"Lỗi truy vấn database subscription: {str(e)}"}), 500

    try:
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
            return jsonify(response_data), 201
        
        response_data["message"] = "Vui lòng thanh toán tiền mặt tại quầy"
        return jsonify(response_data), 201
        
    except Exception as e:
        return jsonify({"error": f"Lỗi tạo giao dịch: {str(e)}"}), 500

@payment_bp.route("/confirm/<int:tx_id>", methods=["POST"])
def confirm_payment(tx_id):
    """Xác nhận thanh toán và tự động gọi User Service nâng cấp gói"""
    payment, message = PaymentService.update_payment_status(
        payment_id=tx_id, 
        status="SUCCESS"
    )

    if message == "NOT_FOUND":
        return jsonify({"error": "Giao dịch không tồn tại"}), 404
    
    if message == "TERMINAL_LOCKED":
        return jsonify({"error": "Giao dịch này đã được xử lý trước đó"}), 400

    if message == "UPDATED":
        return jsonify({
            "message": f"Thành công! Tài khoản đã được nâng cấp lên {payment.package_name}",
            "status": payment.status,
            "package_id": payment.package_id,
            "updated_at": payment.updated_at.strftime("%Y-%m-%d %H:%M:%S") if payment.updated_at else None
        }), 200
    
    return jsonify({"error": "Lỗi hệ thống khi xác nhận thanh toán"}), 500

@payment_bp.route("/history/<string:user_id>", methods=["GET"])
def get_payment_history(user_id):
    """SỬA LỖI 404: Trả về danh sách giao dịch JSON chuẩn cho React"""
    try:
        from models.transaction import Transaction
        transactions = Transaction.query.filter_by(user_id=user_id).order_by(Transaction.created_at.desc()).all()
        return jsonify([tx.to_dict() for tx in transactions]), 200
    except Exception as e:
        return jsonify({"error": f"Lỗi lấy lịch sử: {str(e)}"}), 500

@payment_bp.route("/all", methods=["GET"])
def get_all_payments():
    try:
        from models.transaction import Transaction
        transactions = Transaction.query.order_by(Transaction.created_at.desc()).all()
        return jsonify([tx.to_dict() for tx in transactions]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500