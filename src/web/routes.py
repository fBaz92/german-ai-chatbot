"""Flask routes for the German AI chatbot."""
from __future__ import annotations

from typing import Tuple

from flask import Blueprint, jsonify, make_response, render_template, request

from src.web.game_service import GameService
from src.web.session_store import SESSION_COOKIE_NAME, SessionData, SessionStore

COOKIE_MAX_AGE = 60 * 60 * 24 * 7  # 1 week


def register_routes(app, session_store: SessionStore, game_service: GameService) -> None:
    """Attach all application routes to the Flask app."""
    bp = Blueprint("web", __name__)

    def _get_session() -> Tuple[SessionData, bool]:
        session_id = request.cookies.get(SESSION_COOKIE_NAME)
        return session_store.get_or_create(session_id)

    def _json_response(payload, session: SessionData, created: bool):
        response = jsonify(payload)
        if created:
            response.set_cookie(
                SESSION_COOKIE_NAME,
                session.id,
                max_age=COOKIE_MAX_AGE,
                httponly=True,
                samesite="Lax",
            )
        return response

    @bp.route("/", methods=["GET"])
    def index():
        session, created = _get_session()
        response = make_response(render_template("index.html"))
        if created:
            response.set_cookie(
                SESSION_COOKIE_NAME,
                session.id,
                max_age=COOKIE_MAX_AGE,
                httponly=True,
                samesite="Lax",
            )
        return response

    @bp.route("/health", methods=["GET"])
    def health():
        return jsonify({"status": "ok"})

    @bp.route("/api/config", methods=["GET"])
    def api_config():
        session, created = _get_session()
        data = game_service.get_ui_config()
        return _json_response({"success": True, "config": data}, session, created)

    @bp.route("/api/status", methods=["GET"])
    def api_status():
        session, created = _get_session()
        result = game_service.get_status(session)
        return _json_response(result, session, created)

    @bp.route("/api/start", methods=["POST"])
    def api_start():
        session, created = _get_session()
        payload = request.get_json(silent=True) or {}
        result = game_service.start_game(session, payload)
        return _json_response(result, session, created)

    @bp.route("/api/next", methods=["POST"])
    def api_next():
        session, created = _get_session()
        result = game_service.fetch_next(session)
        return _json_response(result, session, created)

    @bp.route("/api/answer", methods=["POST"])
    def api_answer():
        session, created = _get_session()
        payload = request.get_json(silent=True) or {}
        result = game_service.submit_answer(session, payload)
        return _json_response(result, session, created)

    @bp.route("/api/hint", methods=["POST"])
    def api_hint():
        session, created = _get_session()
        result = game_service.get_hint(session)
        return _json_response(result, session, created)

    @bp.route("/api/reset", methods=["POST"])
    def api_reset():
        session, created = _get_session()
        result = game_service.reset(session)
        return _json_response(result, session, created)

    @bp.route("/api/stats", methods=["GET"])
    def api_stats():
        session, created = _get_session()
        data = game_service.get_stats_payload()
        return _json_response({"success": True, "stats": data}, session, created)

    app.register_blueprint(bp)
