# database.py
from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    # Tạo bảng tự động nếu chưa có
    with app.app_context():
        db.create_all()