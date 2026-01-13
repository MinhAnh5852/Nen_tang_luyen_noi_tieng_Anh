from dotenv import load_dotenv
from flask_cors import CORS

load_dotenv(dotenv_path=".env")

from flask import Flask
from database import db
from config import Config
from controllers.auth_controller import auth_bp
from controllers.user_controller import user_bp
from controllers.internal_controller import internal_bp
from flask_limiter import Limiter
from flask_limiter.util import get_remote_address

def create_app():
    app = Flask(__name__)
    app.config.from_object(Config)
    db.init_app(app)

    CORS(app)  # Enable CORS

    # Add rate limiting
    limiter = Limiter(
        get_remote_address,
        app=app,
        default_limits=["200 per day", "50 per hour"]
    )

    app.register_blueprint(auth_bp)
    app.register_blueprint(user_bp)
    app.register_blueprint(internal_bp)

    @app.route("/health")
    def health():
        try:
            db.session.execute(db.text("SELECT 1"))
            return {"status": "ok"}, 200
        except Exception:
            return {"status": "error"}, 500

    with app.app_context():
        db.create_all()
        print("DB created")
    print("App created")
    return app

app = create_app()
print("App started")
if __name__ == "__main__":
    try:
        app.run(host="0.0.0.0", port=5000)
    except Exception as e:
        print(f"Error running app: {e}")
