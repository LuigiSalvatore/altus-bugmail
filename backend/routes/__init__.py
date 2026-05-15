# ---------------------------------------------------------------------------
# Route Registration
# ---------------------------------------------------------------------------

from backend.routes import config, data, bugs, logs, server_control


def register_routes(app):
    """Register all API route blueprints on the Flask app."""
    app.register_blueprint(config.bp)
    app.register_blueprint(data.bp)
    app.register_blueprint(bugs.bp)
    app.register_blueprint(logs.bp)
    app.register_blueprint(server_control.bp)
