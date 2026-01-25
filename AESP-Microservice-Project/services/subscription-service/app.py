import time
from flask import Flask
from database import db
from config import Config
from controllers.subscription_controller import subscription_bp
from controllers.internal_controller import internal_bp
from sqlalchemy.exc import OperationalError

app = Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

app.register_blueprint(subscription_bp, url_prefix='') 
app.register_blueprint(internal_bp, url_prefix='')

with app.app_context():
    for i in range(5):
        try:
            db.create_all()
            print("Subscription Database connected!")
            break
        except OperationalError:
            print(f"Waiting for Subscription DB... {i}")
            time.sleep(5)

if __name__ == "__main__":
    app.run(host="0.0.0.0", port=5001)