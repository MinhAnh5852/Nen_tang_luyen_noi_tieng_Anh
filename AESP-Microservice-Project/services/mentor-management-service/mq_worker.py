import pika, json, os, time
import pika.exceptions

def callback(ch, method, properties, body):
    # Import bên trong để tránh lỗi Circular Import
    from app import app
    from database import db
    from models.mentor import MentorProfile
    
    try:
        data = json.loads(body)
        if data.get("event") == "USER_REGISTERED" and data.get("role") == "mentor":
            print(f" [!] Nhận tin nhắn: Mentor mới {data.get('email')}")
            
            with app.app_context():
                existing = MentorProfile.query.filter_by(user_id=data.get("user_id")).first()
                if not existing:
                    new_profile = MentorProfile(
                        user_id=data.get("user_id"),
                        username=data.get("username"),
                        email=data.get("email"),
                        status="pending"
                    )
                    db.session.add(new_profile)
                    db.session.commit()
                    print(f" [v] Đã tạo hồ sơ cho: {data.get('email')}")
    except Exception as e:
        print(f" [x] Lỗi xử lý tin nhắn: {e}")

def start_worker():
    # Lấy URL chuẩn từ Docker Compose
    url = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672/')
    
    print(f" [*] Đang kết nối tới RabbitMQ tại: {url}")
    
    for i in range(15): # Tăng lên 15 lần thử cho chắc
        try:
            params = pika.URLParameters(url)
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            
            # Đảm bảo queue tồn tại
            channel.queue_declare(queue='user_events', durable=True)
            
            channel.basic_consume(
                queue='user_events', 
                on_message_callback=callback, 
                auto_ack=True
            )
            
            print(' [*] Mentor Worker ĐANG NGHE RabbitMQ (Queue: user_events)...')
            channel.start_consuming()
            break 
        except Exception as e:
            print(f" [x] RabbitMQ chưa sẵn sàng ({i+1}/15)... Thử lại sau 5s")
            time.sleep(5)

if __name__ == "__main__":
    start_worker()