from flask import Flask
from flask_cors import CORS
from database import db, init_db
import os

app = Flask(__name__)
CORS(app)

app.config['SQLALCHEMY_DATABASE_URI'] = os.environ.get('DATABASE_URL')
app.config['SQLALCHEMY_TRACK_MODIFICATIONS'] = False

# Khởi tạo DB tại đây
init_db(app)

from controllers.mentor_controller import mentor_bp
# Sửa url_prefix thành "/" để tránh lỗi 404 như đã nói ở trên
app.register_blueprint(mentor_bp, url_prefix="/")

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5002)