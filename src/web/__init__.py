"""Flask application factory."""
from __future__ import annotations

import os
from flask import Flask

from src.web.game_service import GameService
from src.web.routes import register_routes
from src.web.session_store import SessionStore


session_store = SessionStore()
game_service = GameService(session_store)


def create_app() -> Flask:
    """Application factory used by both CLI and WSGI servers."""
    app = Flask(
        __name__,
        static_folder="static",
        template_folder="templates",
    )
    app.config["SECRET_KEY"] = os.getenv("FLASK_SECRET_KEY", "german-ai-secret")

    register_routes(app, session_store, game_service)
    return app
