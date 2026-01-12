from flask import Flask
from database import db
from config import Config
from controllers.payment_controller import payment_bp
from controllers.webhook_controller import webhook_bp

app=Flask(__name__)
app.config.from_object(Config)
db.init_app(app)
app.register_blueprint(payment_bp)
app.register_blueprint(webhook_bp)

with app.app_context():
    db.create_all()

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5002)
