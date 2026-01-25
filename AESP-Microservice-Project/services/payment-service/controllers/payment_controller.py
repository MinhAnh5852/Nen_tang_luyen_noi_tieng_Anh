from flask import Blueprint, request, jsonify
from services.payment_service import PaymentService
from models.payment import Payment 
from database import db

payment_bp = Blueprint("payment", __name__)

@payment_bp.route("/checkout", methods=["POST"])
def create_payment():
    data = request.get_json(force=True) or {}
    
    # Kiểm tra các trường bắt buộc bao gồm cả package_id mới
    required = ["user_id", "amount", "method", "package_id"]
    if not all(data.get(k) for k in required):
        return jsonify({"message": "Thiếu thông tin bắt buộc (user_id, amount, method, package_id)"}), 400

    try:
        # Lưu giao dịch kèm theo package_id để biết người dùng mua gói nào
        payment = Payment(
            user_id=data["user_id"],
            amount=data["amount"],
            method=data["method"],
            package_id=data.get("package_id"), # Trường bạn vừa thêm vào Model
            status="PENDING"
        )
        db.session.add(payment)
        db.session.commit()
        
        return jsonify({
            "id": payment.id, 
            "status": payment.status, 
            "checkout_url": f"http://localhost/subscription.html?payment_id={payment.id}"
        }), 201
    except Exception as e:
        return jsonify({"error": "Không thể tạo yêu cầu thanh toán", "details": str(e)}), 500

@payment_bp.route("/my-transactions", methods=["GET"])
def get_my_transactions():
    user_id = request.args.get("user_id")
    if not user_id:
        return jsonify({"message": "Thiếu user_id"}), 400

    try:
        transactions = Payment.query.filter_by(user_id=user_id).order_by(Payment.created_at.desc()).all()
        result = []
        for tx in transactions:
            result.append({
                "id": tx.id,
                "amount": tx.amount,
                "status": tx.status,
                "method": tx.method,
                "date": tx.created_at.strftime("%d/%m/%Y %H:%M")
            })
        return jsonify(result), 200
    except Exception as e:
        return jsonify({"error": "Lỗi truy vấn cơ sở dữ liệu", "details": str(e)}), 500