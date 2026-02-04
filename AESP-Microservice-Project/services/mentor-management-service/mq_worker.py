import pika, json, os, time
import pika.exceptions

def callback(ch, method, properties, body):
    # Import bên trong để tránh lỗi Circular Import
    from app import app
    from database import db
    from models.mentor_model import Mentor # Đảm bảo đúng tên Class Mentor của Bảo
    
    try:
        data = json.loads(body)
        event = data.get("event")
        
        with app.app_context():
            # LUỒNG 1: Tạo hồ sơ mới khi Mentor vừa đăng ký xong
            if event == "USER_REGISTERED" and data.get("role") == "mentor":
                print(f" [!] Nhận tin: Mentor mới đăng ký - {data.get('email')}")
                existing = Mentor.query.filter_by(user_id=data.get("user_id")).first()
                if not existing:
                    new_profile = Mentor(
                        user_id=data.get("user_id"),
                        username=data.get("username"),
                        email=data.get("email"),
                        status="pending" # Mặc định chờ duyệt
                    )
                    db.session.add(new_profile)
                    db.session.commit()
                    print(f" [v] Đã tạo hồ sơ CHỜ DUYỆT cho: {data.get('email')}")
                else:
                    print(f" [!] Hồ sơ đã tồn tại, bỏ qua.")

            # LUỒNG 2: Cập nhật trạng thái khi Admin bấm DUYỆT hoặc TỪ CHỐI (MỚI THÊM)
            elif event == "USER_STATUS_UPDATED":
                user_id = data.get("user_id")
                new_status = data.get("status")
                print(f" [!] Nhận tin: Cập nhật trạng thái Mentor {user_id} -> {new_status}")
                
                mentor = Mentor.query.filter_by(user_id=user_id).first()
                if mentor:
                    mentor.status = new_status
                    db.session.commit()
                    print(f" [v] Đã đồng bộ trạng thái Mentor sang {new_status}")

    except Exception as e:
        print(f" [x] Lỗi xử lý tin nhắn: {e}")

def start_worker():
    # 'rabbitmq' phải khớp với tên service trong docker-compose.yml
    url = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672/')
    print(f" [*] Mentor Worker đang khởi động. Kết nối tới: {url}")
    
    for i in range(20):
        try:
            params = pika.URLParameters(url)
            params.heartbeat = 600
            connection = pika.BlockingConnection(params)
            channel = connection.channel()
            
            channel.queue_declare(queue='user_events', durable=True)
            channel.basic_qos(prefetch_count=1)
            
            # Sử dụng auto_ack=True như cũ của Bảo cho đơn giản
            channel.basic_consume(
                queue='user_events', 
                on_message_callback=callback, 
                auto_ack=True
            )
            
            print(' [*] Mentor Worker ĐANG NGHE RabbitMQ (Queue: user_events)...')
            channel.start_consuming()
            break 
        except Exception as e:
            print(f" [x] RabbitMQ chưa sẵn sàng ({i+1}/20)... Lỗi: {e}")
            time.sleep(5)

if __name__ == "__main__":
    start_worker()