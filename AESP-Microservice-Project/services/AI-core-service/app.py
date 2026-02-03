from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import time
import pika  # Thêm thư viện để kết nối RabbitMQ
import json  # Thêm thư viện để xử lý dữ liệu gửi đi

# Import các service và database
from services.ai_analysis import analyze_speech
from services.speech_to_text import transcribe_audio
from database import db
from models import PracticeSession, ChatHistory

# 1. Load biến môi trường
load_dotenv()

app = Flask(__name__)
# Bật CORS cho toàn bộ ứng dụng để Gateway/Frontend có thể truy cập
CORS(app)

# 2. Cấu hình kết nối Database
db_url = os.environ.get("DATABASE_URL")
if not db_url:
    print("WARNING: DATABASE_URL not found in .env")

app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

# 3. Khởi tạo Database
db.init_app(app)

# --- PHẦN THÊM MỚI 1: HÀM GỬI SỰ KIỆN QUA RABBITMQ ---
def send_practice_event(data):
    """Gửi thông tin luyện tập sang Analytics Service qua RabbitMQ"""
    try:
        # Lấy URL RabbitMQ từ .env (đã được cấu hình trong Docker)
        rabbitmq_url = os.environ.get('RABBITMQ_URL', 'amqp://admin:admin123@app-rabbitmq:5672/')
        params = pika.URLParameters(rabbitmq_url)
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        
        # Khai báo hàng đợi để lưu tin nhắn
        channel.queue_declare(queue='practice_events', durable=True)
        
        # Gửi dữ liệu dưới dạng chuỗi JSON
        channel.basic_publish(
            exchange='',
            routing_key='practice_events',
            body=json.dumps(data),
            properties=pika.BasicProperties(delivery_mode=2) # Đảm bảo tin nhắn không mất khi restart RabbitMQ
        )
        connection.close()
        print(f" [MQ] Đã gửi sự kiện luyện tập cho User {data['user_id']}")
    except Exception as e:
        print(f" [MQ Error] Không thể gửi message: {e}")

# Tự động tạo bảng với cơ chế chờ đợi Database sẵn sàng
with app.app_context():
    for i in range(5):  # Thử lại 5 lần
        try:
            db.create_all()
            print("Database connected and tables created.")
            break
        except Exception as e:
            print(f"Waiting for database... ({i+1}/5). Error: {e}")
            time.sleep(3)

# ✅ SỬA ĐỔI QUAN TRỌNG: Thêm tiền tố /api/ai để khớp với Nginx Gateway
@app.route("/api/ai/chat", methods=["POST"])
def chat():
    """
    Endpoint xử lý hội thoại văn bản và lưu lịch sử.
    """
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON data provided"}), 400

        user_text = data.get("text", "")
        topic = data.get("topic", "General English")
        
        # Lấy user_id dưới dạng UUID/String từ Frontend
        user_id = data.get("user_id", "1")

        if not user_text:
            return jsonify({"error": "No text provided"}), 400
            
        # --- BƯỚC 1: Lưu tin nhắn của User vào DB ---
        user_msg = ChatHistory(user_id=user_id, role="user", message=user_text)
        db.session.add(user_msg)
        
        # --- BƯỚC 2: Gọi AI xử lý ---
        result = analyze_speech(user_text, topic)
        
        if "error" in result:
            db.session.rollback()
            return jsonify(result), 500
            
        # --- BƯỚC 3: Lưu phản hồi của AI vào DB ---
        ai_reply = result.get("reply", "")
        ai_msg = ChatHistory(user_id=user_id, role="ai", message=ai_reply)
        db.session.add(ai_msg)

        # --- BƯỚC 4: Lưu kết quả luyện tập (Score) ---
        accuracy = result.get("accuracy", 0)
        practice = PracticeSession(
            user_id=user_id, 
            topic=topic, 
            accuracy_score=float(accuracy)
        )
        db.session.add(practice)
        
        # Lưu tất cả thay đổi vào MySQL
        db.session.commit()

        # --- PHẦN THÊM MỚI 2: GỬI SỰ KIỆN SANG ANALYTICS SERVICE ---
        # Ngay sau khi lưu DB thành công, gửi tin nhắn đi để đồng bộ Dashboard
        send_practice_event({
            "event": "PRACTICE_COMPLETED",
            "user_id": user_id,
            "accuracy": float(accuracy),
            "topic": topic,
            "duration": 60, # Giả định mỗi lượt chat là 1 phút để tính total_time
            "timestamp": time.time()
        })
            
        return jsonify(result), 200
        
    except Exception as e:
        db.session.rollback()
        print(f"Chat error: {e}")
        return jsonify({"error": str(e)}), 500

# ✅ SỬA ĐỔI QUAN TRỌNG: Thêm tiền tố /api/ai để khớp với Nginx Gateway
@app.route("/api/ai/transcribe", methods=["POST"])
def transcribe():
    """
    Endpoint nhận file âm thanh và chuyển thành văn bản qua Whisper.
    """
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
            
        file = request.files['file']
        
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

        if file:
            result_text = transcribe_audio(file)
            
            if isinstance(result_text, dict) and "error" in result_text:
                return jsonify(result_text), 500
                
            return jsonify({"text": result_text}), 200
            
    except Exception as e:
        print(f"Transcribe error: {e}")
        return jsonify({"error": str(e)}), 500

@app.route("/api/ai/history/<string:user_id>", methods=["GET"])
def get_history(user_id):
    try:
        # Lấy tối đa 30 tin nhắn gần nhất của đúng user_id
        history = ChatHistory.query.filter_by(user_id=user_id)\
            .order_by(ChatHistory.created_at.asc())\
            .limit(30).all()
            
        results = [
            {"sender": h.role, "text": h.message} 
            for h in history
        ]
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500
    
    
if __name__ == "__main__":
    # Chạy trên port 5005 để Gateway điều hướng tới
    app.run(host="0.0.0.0", port=5005)