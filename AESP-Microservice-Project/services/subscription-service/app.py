
from flask import Flask
from database import db
from config import Config
from controllers.subscription_controller import subscription_bp
from controllers.internal_controller import internal_bp

app=Flask(__name__)
app.config.from_object(Config)
db.init_app(app)

app.register_blueprint(subscription_bp)
app.register_blueprint(internal_bp)

with app.app_context():
    db.create_all()

if __name__=="__main__":
    app.run(host="0.0.0.0",port=5001)
