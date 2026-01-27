from flask_sqlalchemy import SQLAlchemy

db = SQLAlchemy()

def init_db(app):
    """
    Khởi tạo kết nối MySQL với các tùy chọn tránh lỗi 'Gone Away'
    và tự động tạo bảng nếu chưa tồn tại.
    """
    db.init_app(app)
    
    # Giữ nguyên các tùy chọn pool để duy trì kết nối bền bỉ với MySQL trong Docker
    app.config['SQLALCHEMY_ENGINE_OPTIONS'] = {
        "pool_recycle": 280,
        "pool_pre_ping": True,
        "pool_size": 10,       # Tăng số lượng kết nối tối đa
        "max_overflow": 20     # Cho phép vượt mức kết nối khi NiFi hoặc User gọi dồn dập
    }

    # THÊM ĐOẠN NÀY: Tự động tạo bảng vào database riêng khi service khởi động
    with app.app_context():
        try:
            db.create_all()
            print(">>> [Payment Service] Database tables initialized successfully.")
        except Exception as e:
            print(f">>> [Payment Service] Database error: {e}")