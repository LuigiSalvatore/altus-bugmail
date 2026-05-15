# ---------------------------------------------------------------------------
# Backend Application Factory
# ---------------------------------------------------------------------------

import os
from flask import Flask, send_from_directory
from backend.routes import register_routes

_BASE_DIR = os.path.dirname(os.path.dirname(os.path.abspath(__file__)))
_WEBAPP_DIR = os.path.join(_BASE_DIR, 'webapp')


def create_app():
    """Create and configure the Flask application."""
    app = Flask(__name__, static_folder=_WEBAPP_DIR, static_url_path='')

    # Register all API route blueprints
    register_routes(app)

    # Serve the frontend
    @app.route('/')
    def index():
        return send_from_directory(_WEBAPP_DIR, 'index.html')

    return app
