
from flask import Blueprint,jsonify
internal_bp=Blueprint("internal",__name__)
@internal_bp.route("/internal/verify",methods=["GET"])
def verify():
    return jsonify({"valid":True})
