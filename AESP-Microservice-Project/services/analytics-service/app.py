from flask import Flask, jsonify
import requests
import os
from dotenv import load_dotenv

load_dotenv()

app = Flask(__name__)

USER_SERVICE_URL = os.getenv("USER_SERVICE_URL")
PAYMENT_SERVICE_URL = os.getenv("PAYMENT_SERVICE_URL")

@app.route("/analytics/dashboard")
def dashboard():
    # 1. Lấy dữ liệu user
    try:
        users = requests.get(f"{USER_SERVICE_URL}/users").json()
        # API user trả về list, nếu trả về dict wrap thì cần sửa lại logic này
        total_users = len(users) 
    except:
        total_users = 0 # Fallback nếu user-service chết

    # 2. Lấy dữ liệu payment
    try:
        # Giả sử API payment trả về list các giao dịch
        payments = requests.get(f"{PAYMENT_SERVICE_URL}/payments").json()
        total_revenue = sum(p.get("amount", 0) for p in payments) if isinstance(payments, list) else 0
        total_payments = len(payments) if isinstance(payments, list) else 0
    except:
        total_revenue = 0
        total_payments = 0

    # 3. Trả về kết quả tổng hợp
    return jsonify({
        "total_users": total_users,
        "total_payments": total_payments,
        "total_revenue": total_revenue,
        "status": "success"
    })

@app.route("/health")
def health():
    return {"status": "analytics-service running"}

if __name__ == "__main__":
    # Chạy ở port 5000 bên trong container
    app.run(host="0.0.0.0", port=5000)