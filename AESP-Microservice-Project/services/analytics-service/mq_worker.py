import pika
import json
import os
import time
from app import app
from database import db
from models import SystemStat, ActivityLog

def update_stat(key, increment=1):
    """Cập nhật giá trị thống kê (cộng dồn)"""
    with app.app_context():
        stat = SystemStat.query.get(key)
        if not stat:
            # Nếu chưa có thì khởi tạo (dùng 0.0 để hỗ trợ cả số thực cho tiền)
            stat = SystemStat(key=key, value=0.0)
            db.session.add(stat)
        
        stat.value += float(increment)
        db.session.commit()

def log_activity(message):
    """Lưu nhật ký hoạt động mới nhất"""
    with app.app_context():
        new_log = ActivityLog(message=message)
        db.session.add(new_log)
        db.session.commit()

def callback(ch, method, properties, body):
    try:
        data = json.loads(body)
        event = data.get("event")
        email = data.get("email", "N/A")
        
        # 1. Thống kê Người dùng
        if event in ["USER_REGISTERED", "USER_REGISTERED_VIA_FIREBASE"]:
            update_stat("total_users")
            log_activity(f"Người dùng mới: {email}")
            print(f" [v] Đã đếm 1 User mới: {email}")

        # 2. Thống kê Mentor đang hoạt động (Khi Admin duyệt)
        elif event == "MENTOR_APPROVED":
            update_stat("active_mentors")
            log_activity(f"Mentor đã được duyệt: {email}")
            print(f" [v] Đã tăng số lượng Mentor hoạt động: {email}")

        # 3. Thống kê Doanh thu (Khi Learner mua gói)
        elif event == "PAYMENT_SUCCESS":
            amount = data.get("amount", 0)
            update_stat("total_revenue", amount)
            log_activity(f"Doanh thu mới: +{amount:,} VND từ {email}")
            print(f" [v] Đã cộng {amount} vào tổng doanh thu.")

        ch.basic_ack(delivery_tag=method.delivery_tag)
    except Exception as e:
        print(f" [x] Lỗi xử lý tin nhắn: {e}")
        # Không ack để tin nhắn không bị mất nếu lỗi hệ thống
        ch.basic_nack(delivery_tag=method.delivery_tag, requeue=False)

def start_worker():
    url = os.environ.get('RABBITMQ_URL', 'amqp://guest:guest@rabbitmq:5672/')
    
    # Thử kết nối lại nếu RabbitMQ chưa khởi động kịp
    while True:
        try:
            connection = pika.BlockingConnection(pika.URLParameters(url))
            channel = connection.channel()
            
            # Khai báo queue (phải khớp với tên bên User Service gửi)
            channel.queue_declare(queue='user_events', durable=True)
            
            # Chỉ nhận 1 tin nhắn mỗi lần để xử lý ổn định
            channel.basic_qos(prefetch_count=1)
            channel.basic_consume(queue='user_events', on_message_callback=callback)
            
            print(" [*] Analytic Worker đang hóng tin nhắn (User, Mentor, Revenue)...")
            channel.start_consuming()
        except pika.exceptions.AMQPConnectionError:
            print(" [!] Chưa kết nối được RabbitMQ, thử lại sau 5s...")
            time.sleep(5)
        except Exception as e:
            print(f" [!] Lỗi Worker: {e}")
            time.sleep(5)

if __name__ == "__main__":
    start_worker()