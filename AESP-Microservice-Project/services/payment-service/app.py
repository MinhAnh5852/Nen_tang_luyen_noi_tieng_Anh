import os
from flask import Flask
from flask_cors import CORS
from database import db, init_db
from config import Config

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    
    init_db(app)
    # CORS(app)

    with app.app_context():
        from models.transaction import Transaction
        db.create_all() # Tự động tạo bảng transactions trong MySQL

    from controllers.payment_controller import payment_bp
    app.register_blueprint(payment_bp, url_prefix='/api/payments')

    return app

app = create_app()

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5004)