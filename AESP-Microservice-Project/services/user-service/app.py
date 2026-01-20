import os
import pika
import json
from dotenv import load_dotenv
from flask_cors import CORS
from flask import Flask
from database import db
from config import Config
from controllers.auth_controller import auth_bp
from controllers.user_controller import user_bp
from controllers.internal_controller import internal_bp
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

load_dotenv(dotenv_path=".env")

# --- HÀM BỔ SUNG: GỬI TIN NHẮN SANG RABBITMQ ---
def publish_user_event(user_data):
    try:
        # Lấy thông tin từ biến môi trường (khớp với docker-compose)
        user = os.getenv("RABBITMQ_USER", "admin")
        password = os.getenv("RABBITMQ_PASS", "admin123")
        host = os.getenv("RABBITMQ_HOST", "app-rabbitmq")
        
        credentials = pika.PlainCredentials(user, password)
        connection = pika.BlockingConnection(
            pika.ConnectionParameters(host=host, credentials=credentials)
        )
        channel = connection.channel()

        # Khai báo hàng đợi (durable=True để không mất tin nhắn khi rabbitmq restart)
        channel.queue_declare(queue='analytics_queue', durable=True)

        # Gửi dữ liệu dưới dạng JSON
        message = json.dumps(user_data)
        channel.basic_publish(
            exchange='',
            routing_key='analytics_queue',
            body=message,
            properties=pika.BasicProperties(delivery_mode=2) # Tin nhắn bền vững
        )
        print(f" [x] Đã gửi sự kiện tới Analytics: {message}")
        connection.close()
    except Exception as e:
        print(f" !!! Không thể gửi tin nhắn tới RabbitMQ: {e}")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    CORS(app)

    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["2000 per day", "500 per hour"]
    )

    # Đưa hàm publish vào app để các controller có thể sử dụng (tùy chọn)
    app.publish_user_event = publish_user_event

    app.register_blueprint(auth_bp, url_prefix='/auth')
    app.register_blueprint(user_bp, url_prefix='/users')
    app.register_blueprint(internal_bp)

    @app.route("/health")
    def health():
        try:
            db.session.execute(db.text("SELECT 1"))
            return {"status": "ok"}, 200
        except Exception:
            return {"status": "error"}, 500

    with app.app_context():
        db.create_all()
        print("DB created")
    
    print("App created")
    return app

app = create_app()

# --- LƯU Ý QUAN TRỌNG ---
# Bạn cần gọi hàm `publish_user_event({"event": "new_user", "username": "..."})` 
# bên trong file `controllers/auth_controller.py` hoặc nơi xử lý logic Register 
# ngay sau khi `db.session.commit()` thành công.

if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000)
    except Exception as e:
        print(f"Error running app: {e}")