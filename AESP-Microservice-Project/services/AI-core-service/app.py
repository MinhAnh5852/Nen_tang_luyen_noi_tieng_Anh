from flask import Flask, request, jsonify
from flask_cors import CORS
from dotenv import load_dotenv
import os
import time
import pika
import json

# Import các service và database
from services.ai_analysis import analyze_speech
from services.speech_to_text import transcribe_audio
from database import db
from models import PracticeSession, ChatHistory

load_dotenv()

app = Flask(__name__)
CORS(app)

# --- CẤU HÌNH DATABASE ---
db_url = os.environ.get("DATABASE_URL")
app.config["SQLALCHEMY_DATABASE_URI"] = db_url
app.config["SQLALCHEMY_TRACK_MODIFICATIONS"] = False

db.init_app(app)

# --- PHẦN 1: TỐI ƯU RABBITMQ (SỬA LỖI TREO API) ---
def send_practice_event(data):
    """Gửi sự kiện sang Analytics Service. Không được làm sập hàm chat chính."""
    try:
        # Lấy URL từ env, mặc định trỏ về service 'rabbitmq' trong docker-compose
        rabbitmq_url = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672/')
        
        # Thiết lập timeout 2 giây để tránh treo API Chat nếu RabbitMQ sập
        params = pika.URLParameters(rabbitmq_url)
        params.socket_timeout = 2 
        
        connection = pika.BlockingConnection(params)
        channel = connection.channel()
        
        channel.queue_declare(queue='practice_events', durable=True)
        
        channel.basic_publish(
            exchange='',
            routing_key='practice_events',
            body=json.dumps(data),
            properties=pika.BasicProperties(delivery_mode=2)
        )
        connection.close()
        print(f" [MQ Success] User {data['user_id']} event sent.")
    except Exception as e:
        # Quan trọng: Chỉ in lỗi ra log, vẫn để hàm chat() chạy tiếp
        print(f" [MQ Error] RabbitMQ connection failed: {e}")

# Tự động tạo bảng (Retry logic)
with app.app_context():
    for i in range(5):
        try:
            db.create_all()
            print("Database connected successfully.")
            break
        except Exception as e:
            print(f"Waiting for database... ({i+1}/5)")
            time.sleep(3)

# --- PHẦN 2: CÁC ENDPOINT API ---

@app.route("/api/ai/chat", methods=["POST"])
def chat():
    try:
        data = request.json
        if not data:
            return jsonify({"error": "No JSON provided"}), 400

        user_text = data.get("text", "")
        topic = data.get("topic", "General English")
        user_id = str(data.get("user_id", "1"))

        if not user_text:
            return jsonify({"error": "No text provided"}), 400
            
        # 1. Gọi AI xử lý trước (Để nếu AI lỗi thì chưa lưu DB vội)
        result = analyze_speech(user_text, topic)
        if "error" in result:
             return jsonify(result), 500

        # 2. Lưu lịch sử và kết quả vào DB
        try:
            # Tin nhắn của User
            user_msg = ChatHistory(user_id=user_id, role="user", message=user_text)
            db.session.add(user_msg)
            
            # Phản hồi của AI
            ai_reply = result.get("reply", "")
            ai_msg = ChatHistory(user_id=user_id, role="ai", message=ai_reply)
            db.session.add(ai_msg)

            # Kết quả luyện tập
            accuracy = result.get("accuracy", 0)
            practice = PracticeSession(
                user_id=user_id, 
                topic=topic, 
                accuracy_score=float(accuracy)
            )
            db.session.add(practice)
            
            db.session.commit()
        except Exception as db_e:
            db.session.rollback()
            print(f"Database Error: {db_e}")
            # Vẫn trả về kết quả AI cho người dùng dù lưu DB lỗi
        
        # 3. Gửi sự kiện Async sang Analytics (Chạy ngầm)
        send_practice_event({
            "event": "PRACTICE_COMPLETED",
            "user_id": user_id,
            "accuracy": float(result.get("accuracy", 0)),
            "topic": topic,
            "duration": 60,
            "timestamp": time.time()
        })
            
        return jsonify(result), 200
        
    except Exception as e:
        print(f"!!! CRITICAL CHAT ERROR: {e}")
        return jsonify({"error": "Internal Server Error"}), 500

@app.route("/api/ai/transcribe", methods=["POST"])
def transcribe():
    try:
        if 'file' not in request.files:
            return jsonify({"error": "No file part"}), 400
        file = request.files['file']
        if file.filename == '':
            return jsonify({"error": "No selected file"}), 400

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
        history = ChatHistory.query.filter_by(user_id=user_id)\
            .order_by(ChatHistory.created_at.asc())\
            .limit(30).all()
        results = [{"sender": h.role, "text": h.message} for h in history]
        return jsonify(results), 200
    except Exception as e:
        return jsonify({"error": str(e)}), 500

@app.route('/api/ai/submissions/for-mentor/<string:mentor_id>', methods=['GET'])
def get_submissions_for_mentor(mentor_id):
    try:
        from sqlalchemy import text
        # Lưu ý: Truy vấn cross-db yêu cầu user-db và xdpm nằm cùng instance MySQL
        query = text("""
            SELECT p.id, p.user_id, u.username, p.topic, p.created_at as date, 
                   p.accuracy_score as ai_score, p.ai_feedback
            FROM xdpm.practice_sessions p
            JOIN user_db.mentor_selections ms ON p.user_id = ms.learner_id
            JOIN user_db.users u ON p.user_id = u.id
            WHERE ms.mentor_id = :mid AND ms.status = 'active'
            ORDER BY p.created_at DESC
        """)
        result = db.session.execute(query, {"mid": mentor_id}).mappings().all()
        return jsonify([dict(row) for row in result]), 200
    except Exception as e:
        print(f"Mentor Submissions Error: {e}")
        return jsonify({"error": str(e)}), 500 

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5005)