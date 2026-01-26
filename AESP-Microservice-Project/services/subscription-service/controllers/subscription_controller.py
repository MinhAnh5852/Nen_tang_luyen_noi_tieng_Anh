from flask import Blueprint, jsonify, request
from models.subscription import SubscriptionPlan 
from database import db

sub_bp = Blueprint("subscription", __name__)

# 1. Lấy danh sách gói
@sub_bp.route("/plans", methods=["GET"])
def get_plans():
    try:
        plans = SubscriptionPlan.query.all()
        return jsonify([p.to_dict() for p in plans]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

# 2. Tạo gói mới
@sub_bp.route("/plans", methods=["POST"])
def create_plan():
    data = request.get_json()
    try:
        raw_features = data.get('features', '')
        if isinstance(raw_features, list):
            raw_features = ",".join(raw_features)

        new_plan = SubscriptionPlan(
            name=data.get('name'),
            price=data.get('price'),
            duration_days=data.get('duration_days', 30),
            badge_text=data.get('badge_text', ''),
            features=raw_features,
            is_active=True
        )
        db.session.add(new_plan)
        db.session.commit()
        return jsonify(new_plan.to_dict()), 201
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# 3. Cập nhật gói (MỚI THÊM)
@sub_bp.route("/plans/<string:id>", methods=["PUT"])
def update_plan(id):
    data = request.get_json()
    plan = db.session.get(SubscriptionPlan, id)
    if not plan:
        return jsonify({"message": "Không tìm thấy gói"}), 404
    
    try:
        plan.name = data.get('name', plan.name)
        plan.price = data.get('price', plan.price)
        plan.badge_text = data.get('badge_text', plan.badge_text)
        
        # Xử lý features tương tự như khi tạo mới
        features = data.get('features', plan.features)
        if isinstance(features, list):
            features = ",".join(features)
        plan.features = features
        
        db.session.commit()
        return jsonify(plan.to_dict()), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 400

# 4. Bật/Tắt gói
@sub_bp.route("/plans/toggle/<string:id>", methods=["POST"])
def toggle_plan(id):
    plan = db.session.get(SubscriptionPlan, id)
    if not plan:
        return jsonify({"message": "Không tìm thấy gói"}), 404
    
    plan.is_active = not plan.is_active
    db.session.commit()
    return jsonify({"message": "Thành công", "is_active": plan.is_active}), 200

# 5. Xóa gói (Đã có sẵn của bạn)
@sub_bp.route("/plans/<string:id>", methods=["DELETE"])
def delete_plan(id):
    plan = db.session.get(SubscriptionPlan, id)
    if not plan:
        return jsonify({"message": "Không tồn tại"}), 404
    try:
        db.session.delete(plan)
        db.session.commit()
        return jsonify({"message": "Đã xóa"}), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500