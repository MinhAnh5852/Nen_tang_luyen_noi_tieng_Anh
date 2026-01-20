import pika
import os
import json
import threading
import time
from flask import Flask, jsonify
from flask_cors import CORS

app = Flask(__name__)
CORS(app)

# Biến toàn cục lưu trữ số liệu
stats = {
    "total_users": 0,
    "total_payments": 0,
    "total_revenue": 0
}

# --- 1. HÀM XỬ LÝ TIN NHẮN ---
def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(f" [x] Analytics nhận được: {data}")
        
        event_type = data.get("event")
        if event_type == "new_user":
            stats["total_users"] += 1
            print(f" [!] Cập nhật: total_users = {stats['total_users']}")
        
        elif event_type == "new_payment":
            amount = data.get("amount", 0)
            stats["total_payments"] += 1
            stats["total_revenue"] += amount
            print(f" [!] Cập nhật: doanh thu +{amount}")

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f" !!! Lỗi xử lý tin nhắn: {e}")

# --- 2. HÀM CHẠY RABBITMQ CONSUMER ---
def start_rabbitmq_consumer():
    rabbitmq_host = os.getenv("RABBITMQ_HOST", "app-rabbitmq")
    rabbitmq_user = os.getenv("RABBITMQ_USER", "admin")
    rabbitmq_pass = os.getenv("RABBITMQ_PASS", "admin123")
    
    # Đợi một chút để đảm bảo mạng Docker đã sẵn sàng
    time.sleep(5)
    
    while True:
        try:
            print(f" [*] Đang thiết lập kết nối tới: {rabbitmq_host} (User: {rabbitmq_user})")
            credentials = pika.PlainCredentials(rabbitmq_user, rabbitmq_pass)
            
            # Cấu hình kết nối an toàn
            parameters = pika.ConnectionParameters(
                host=rabbitmq_host,
                credentials=credentials,
                heartbeat=60, # Giảm xuống 60 để phát hiện mất kết nối nhanh hơn
                blocked_connection_timeout=30
            )
            
            connection = pika.BlockingConnection(parameters)
            channel = connection.channel()
            
            channel.queue_declare(queue='analytics_queue', durable=True)
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='analytics_queue', on_message_callback=callback)

            print(f" [OK] KẾT NỐI THÀNH CÔNG! Đang lắng nghe...")
            channel.start_consuming()
            
        except Exception as e:
            print(f" !!! Kết nối thất bại hoặc bị ngắt: {e}. Thử lại sau 5 giây...")
            time.sleep(5)

# --- 3. CÁC ROUTE API ---
@app.route("/dashboard")
def dashboard():
    return jsonify({
        "status": "success",
        "total_users": stats["total_users"],
        "total_payments": stats["total_payments"],
        "total_revenue": stats["total_revenue"]
    })

@app.route("/health")
def health():
    return {"status": "ok", "service": "analytics"}

# --- 4. KHỞI CHẠY ---
if __name__ == "__main__":
    # KHỞI CHẠY THREAD Ở ĐÂY
    # Daemon=True để thread tự đóng khi app chính đóng
    t = threading.Thread(target=start_rabbitmq_consumer, daemon=True)
    t.start()
    
    # Chạy Flask Server (Bắt buộc debug=False trong Docker khi dùng Thread)
    app.run(host="0.0.0.0", port=5000, debug=False)