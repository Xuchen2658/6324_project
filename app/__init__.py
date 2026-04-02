from flask import Flask
from flask_cors import CORS

from app.config.settings import UPLOAD_DIR
from app.core.database import init_db
from app.routes import register_routes


def create_app():
    app = Flask(__name__, template_folder="../templates", static_folder="../static")
    app.secret_key = "change_this_to_a_random_secret_key"

    CORS(app)

    UPLOAD_DIR.mkdir(parents=True, exist_ok=True)
    init_db()
    register_routes(app)

    return app