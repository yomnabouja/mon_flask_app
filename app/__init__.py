from flask import Flask
from .routes import api_routes

def create_app():
    app = Flask(__name__)
    app.secret_key = 'mon_super_secret_pour_la_session_123!'  # pour sessions/login
    app.register_blueprint(api_routes)
    return app