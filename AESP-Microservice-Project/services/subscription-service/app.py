from flask import Flask, jsonify
from flask_cors import CORS
from config import Config
from database import db, init_db
import logging
import os
from dotenv import load_dotenv

load_dotenv()
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger("SubscriptionService")

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    CORS(app)
    init_db(app)
    
    # 1. Đăng ký Blueprints ngay tại đây (Trước khi tạo bảng)
    try:
        from controllers.subscription_controller import sub_bp
        from controllers.internal_controller import internal_bp
        
        # Thống nhất prefix để Nginx Gateway trỏ vào đúng
        app.register_blueprint(sub_bp, url_prefix='/')
        app.register_blueprint(internal_bp, url_prefix='/api/internal')
        
        logger.info(">>> Blueprints registered successfully!")
    except Exception as e:
        logger.error(f">>> Blueprint Registration Error: {e}")

    # 2. Route Health Check để test Gateway
    @app.route('/api/subscriptions/health', methods=['GET'])
    def health_check():
        return jsonify({
            "status": "Subscription Service is running", 
            "port": 5001,
            "database": "connected"
        }), 200

    # 3. Tự động tạo bảng (Nên để cuối cùng)
    with app.app_context():
        try:
            from models.subscription import SubscriptionPlan
            db.create_all()
            logger.info(">>> Database tables verified for subscription_plans!")
        except Exception as e:
            logger.error(f">>> Database Creation Error: {e}")

    return app

app = create_app()

if __name__ == "__main__":
    # Luôn bật Debug=True ở local để soi lỗi
    app.run(host="0.0.0.0", port=5001, debug=True)