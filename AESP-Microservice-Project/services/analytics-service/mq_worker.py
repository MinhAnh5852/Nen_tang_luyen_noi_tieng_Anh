# analytics-service/mq_worker.py
import pika
import json
import os
import time
from app import app, db
from models import PracticeSession

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        print(f" [x] Nhận sự kiện luyện tập: {data}")

        with app.app_context():
            # Đảm bảo ép kiểu dữ liệu chuẩn trước khi lưu
            new_session = PracticeSession(
                user_id=str(data.get('user_id')),
                topic=data.get('topic', 'General English'),
                accuracy_score=float(data.get('accuracy', 0)),
                duration_seconds=int(data.get('duration', 60))
            )
            
            db.session.add(new_session)
            db.session.commit()
            print(f" [OK] Đã lưu tiến độ vào analytics_db cho User: {data.get('user_id')}")

        ch.basic_ack(delivery_tag=method.delivery_tag)
        
    except Exception as e:
        print(f" [Error] Lỗi xử lý tin nhắn: {e}")
        with app.app_context():
            db.session.rollback()

def start_worker():
    # SỬA TẠI ĐÂY: Ưu tiên lấy từ .env đã cấu hình amqp://guest:guest@rabbitmq:5672/
    # Chỉ dùng giá trị mặc định nếu biến môi trường hoàn toàn trống
    rabbitmq_url = os.environ.get('RABBITMQ_URL')
    if not rabbitmq_url:
        rabbitmq_url = 'amqp://guest:guest@rabbitmq:5672/'
    
    print(f" [*] Đang kết nối tới RabbitMQ tại: {rabbitmq_url}")

    connection = None
    for i in range(10):
        try:
            params = pika.URLParameters(rabbitmq_url)
            # Thêm heartbeat để duy trì kết nối ổn định trong Docker
            params.heartbeat = 600
            params.blocked_connection_timeout = 300
            
            connection = pika.BlockingConnection(params)
            break
        except Exception as e:
            print(f" Đang đợi RabbitMQ khởi động... ({i+1}/10) - Lỗi: {e}")
            time.sleep(5)

    if not connection:
        print(" [!] Không thể kết nối tới RabbitMQ. Worker dừng hoạt động.")
        return

    channel = connection.channel()
    # Khai báo hàng đợi trùng với queue_declare của AI Service
    channel.queue_declare(queue='practice_events', durable=True)
    channel.basic_qos(prefetch_count=1)
    channel.basic_consume(queue='practice_events', on_message_callback=callback)

    print(' [*] Analytics Worker đang chờ tin nhắn. Nhấn Ctrl+C để thoát.')
    channel.start_consuming()

if __name__ == "__main__":
    start_worker()