from flask_sqlalchemy import SQLAlchemy
import os

db = SQLAlchemy()

def init_db(app):
    db.init_app(app)
    # Thêm dòng này để chắc chắn bảng được tạo
    with app.app_context():
        from models.mentor import MentorProfile # Phải import model ở đây
        db.create_all()
        print(">>> [Mentor Service]: Đã kiểm tra và tạo bảng mentor_profiles thành công.")