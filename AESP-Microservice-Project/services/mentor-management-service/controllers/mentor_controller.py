from flask import Blueprint, jsonify, request
from models.mentor import MentorProfile
from database import db

mentor_bp = Blueprint("mentor", __name__)

@mentor_bp.route("/profiles", methods=["GET"])
def get_mentors():
    try:
        profiles = MentorProfile.query.all()
        return jsonify([p.to_dict() for p in profiles]), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@mentor_bp.route("/verify/<string:id>", methods=["POST"])
def verify_mentor(id):
    try:
        data = request.get_json()
        action = data.get("action") 
        
        profile = db.session.get(MentorProfile, id)
        
        if not profile:
            return jsonify({"message": "Không tìm thấy hồ sơ"}), 404
        
        # Chuyển đổi trạng thái dựa trên action
        if action == 'approve':
            profile.status = 'active'
        elif action == 'reject':
            profile.status = 'rejected'
        else:
            return jsonify({"message": "Hành động không hợp lệ"}), 400
            
        db.session.commit()
        return jsonify({
            "message": f"Cập nhật thành công: {profile.status}",
            "status": profile.status
        }), 200
    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500