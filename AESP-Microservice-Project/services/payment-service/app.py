import time
from flask import Flask
from database import db
from config import Config
from controllers.payment_controller import payment_bp
from controllers.webhook_controller import webhook_bp
from sqlalchemy.exc import OperationalError

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    # Đăng ký Blueprint không có prefix để khớp với Nginx
    app.register_blueprint(payment_bp, url_prefix='') 
    app.register_blueprint(webhook_bp, url_prefix='')

    # Cơ chế Retry: Đợi Database khởi động xong (Tối đa 5 lần)
    with app.app_context():
        retries = 5
        while retries > 0:
            try:
                db.create_all()
                print("Database connected and tables created!")
                break
            except OperationalError:
                retries -= 1
                print(f"Waiting for database... ({retries} retries left)")
                time.sleep(5)
        if retries == 0:
            print("Could not connect to database. Exiting.")
    
    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)