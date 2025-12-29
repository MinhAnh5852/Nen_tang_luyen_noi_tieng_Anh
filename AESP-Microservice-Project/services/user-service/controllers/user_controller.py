from flask import Blueprint,request,jsonify
from database import db
from models.user import User
from werkzeug.security import generate_password_hash

user_bp=Blueprint("users",__name__)
@user_bp.route("/users/register",methods=["POST"])
def register():
    d=request.json
    u=User(email=d["email"],password=generate_password_hash(d["password"]),role=d["role"])
    db.session.add(u);db.session.commit()
    return jsonify({"id":u.id})
