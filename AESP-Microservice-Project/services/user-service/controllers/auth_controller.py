
from flask import Blueprint,request,jsonify
from services.auth_service import AuthService

auth_bp=Blueprint("auth",__name__)
@auth_bp.route("/auth/login",methods=["POST"])
def login():
    d=request.json
    return jsonify({"token":AuthService().login(d["email"],d["password"])})
