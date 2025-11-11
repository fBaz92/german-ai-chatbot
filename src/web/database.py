"""Database utilities for tracking mistakes and stats."""
from __future__ import annotations

import logging
import os
import json
from typing import Any, Dict, List, Optional

from sqlalchemy import create_engine, text
from sqlalchemy.engine import Engine
from sqlalchemy.exc import SQLAlchemyError

logger = logging.getLogger(__name__)


class StatsRepository:
    """Persists mistake stats in PostgreSQL when configured."""

    def __init__(self):
        self.database_url = os.getenv("DATABASE_URL")
        self.engine: Optional[Engine] = None
        self.enabled = bool(self.database_url)

        if self.enabled:
            self._connect()

    def _connect(self) -> None:
        """Establish DB connection and ensure schema."""
        try:
            self.engine = create_engine(
                self.database_url,
                pool_pre_ping=True,
                future=True,
            )
            self._ensure_schema()
            logger.info("Connected to PostgreSQL for stats tracking.")
        except SQLAlchemyError as exc:
            logger.warning("PostgreSQL unavailable (%s). Running without stats.", exc)
            self.engine = None
            self.enabled = False

    def _ensure_schema(self) -> None:
        """Create required tables if they don't exist."""
        if not self.engine:
            return

        statements = [
            """
            CREATE TABLE IF NOT EXISTS schema_info (
                id SERIAL PRIMARY KEY,
                schema_version INTEGER NOT NULL,
                created_at TIMESTAMPTZ DEFAULT NOW()
            )
            """,
            """
            CREATE TABLE IF NOT EXISTS mistake_items (
                id SERIAL PRIMARY KEY,
                game_mode TEXT NOT NULL,
                item_key TEXT NOT NULL,
                item_display TEXT NOT NULL,
                item_type TEXT NOT NULL,
                wrong_count INTEGER NOT NULL DEFAULT 0,
                correct_count INTEGER NOT NULL DEFAULT 0,
                last_wrong_at TIMESTAMPTZ,
                last_correct_at TIMESTAMPTZ,
                UNIQUE (game_mode, item_key)
            )
            """,
            "ALTER TABLE mistake_items ADD COLUMN IF NOT EXISTS context JSONB DEFAULT '{}'::jsonb",
        ]
        with self.engine.begin() as conn:
            for stmt in statements:
                conn.execute(text(stmt))

        logger.info("Stats tables ready.")

    def is_available(self) -> bool:
        """Return True if DB is connected and schema ready."""
        return bool(self.engine)

    def record_attempt(
        self,
        game_mode: str,
        item_key: str,
        item_display: str,
        item_type: str,
        is_correct: bool,
        context: Optional[Dict[str, Any]] = None,
    ) -> None:
        """Upsert stats for a single attempt."""
        if not self.engine:
            return

        query = text(
            """
            INSERT INTO mistake_items (
                game_mode, item_key, item_display, item_type,
                wrong_count, correct_count, last_wrong_at, last_correct_at, context
            ) VALUES (
                :game_mode, :item_key, :item_display, :item_type,
                CASE WHEN :is_correct THEN 0 ELSE 1 END,
                CASE WHEN :is_correct THEN 1 ELSE 0 END,
                CASE WHEN :is_correct THEN NULL ELSE NOW() END,
                CASE WHEN :is_correct THEN NOW() ELSE NULL END,
                COALESCE(CAST(:context_json AS JSONB), '{}'::jsonb)
            )
            ON CONFLICT (game_mode, item_key) DO UPDATE
            SET wrong_count = mistake_items.wrong_count + CASE WHEN EXCLUDED.wrong_count > 0 THEN 1 ELSE 0 END,
                correct_count = mistake_items.correct_count + CASE WHEN EXCLUDED.correct_count > 0 THEN 1 ELSE 0 END,
                last_wrong_at = CASE
                    WHEN EXCLUDED.last_wrong_at IS NOT NULL THEN EXCLUDED.last_wrong_at
                    ELSE mistake_items.last_wrong_at
                END,
                last_correct_at = CASE
                    WHEN EXCLUDED.last_correct_at IS NOT NULL THEN EXCLUDED.last_correct_at
                    ELSE mistake_items.last_correct_at
                END,
                context = COALESCE(mistake_items.context, '{}'::jsonb) || COALESCE(EXCLUDED.context, '{}'::jsonb)
            """
        )

        params = {
            "game_mode": game_mode,
            "item_key": item_key,
            "item_display": item_display,
            "item_type": item_type,
            "is_correct": is_correct,
            "context_json": json.dumps(context) if context else None,
        }

        try:
            with self.engine.begin() as conn:
                conn.execute(query, params)
        except SQLAlchemyError as exc:
            logger.warning("Failed to record attempt: %s", exc)

    def get_focus_item(self, game_mode: str) -> Optional[Dict[str, Any]]:
        """Return the most-missed item for the given game."""
        if not self.engine:
            return None

        query = text(
            """
            SELECT game_mode, item_key, item_display, item_type, wrong_count, correct_count, context
            FROM mistake_items
            WHERE game_mode = :game_mode AND wrong_count > 0
            ORDER BY wrong_count DESC, correct_count ASC
            LIMIT 1
            """
        )
        try:
            with self.engine.begin() as conn:
                row = conn.execute(query, {"game_mode": game_mode}).mappings().first()
                if not row:
                    return None
                result = dict(row)
                context = result.get("context")
                if isinstance(context, str):
                    result["context"] = json.loads(context)
                return result
        except SQLAlchemyError as exc:
            logger.warning("Failed to fetch focus item: %s", exc)
            return None

    def get_dashboard(self, limit: int = 5) -> Dict[str, Any]:
        """Return summary metrics and top mistakes for display."""
        if not self.engine:
            return {"available": False, "summary": [], "topMistakes": {}, "reviewCount": 0}

        summary_sql = text(
            """
            SELECT
                game_mode,
                SUM(correct_count + wrong_count) AS attempts,
                SUM(correct_count) AS correct,
                SUM(wrong_count) AS wrong
            FROM mistake_items
            GROUP BY game_mode
            ORDER BY game_mode
            """
        )

        mistakes_sql = text(
            """
            SELECT game_mode, item_key, item_display, item_type, wrong_count, correct_count, context
            FROM mistake_items
            WHERE wrong_count > 0
            ORDER BY wrong_count DESC, correct_count ASC
            LIMIT :limit
            """
        )
        total_sql = text("SELECT COUNT(*) FROM mistake_items WHERE wrong_count > 0")

        try:
            with self.engine.begin() as conn:
                summary_rows = conn.execute(summary_sql).mappings().all()
                mistakes_rows = conn.execute(mistakes_sql, {"limit": limit}).mappings().all()
                total_count = conn.execute(total_sql).scalar() or 0
        except SQLAlchemyError as exc:
            logger.warning("Failed to load stats: %s", exc)
            return {"available": False, "summary": [], "topMistakes": {}, "reviewCount": 0}

        top_by_game: Dict[str, List[Dict[str, Any]]] = {}
        for row in mistakes_rows:
            item = dict(row)
            context = item.get("context")
            if isinstance(context, str):
                item["context"] = json.loads(context)
            top_by_game.setdefault(item["game_mode"], []).append(item)

        return {
            "available": True,
            "summary": [dict(row) for row in summary_rows],
            "topMistakes": top_by_game,
            "reviewCount": total_count,
        }

    def get_review_items(self, limit: int = 10, game_mode: Optional[str] = None) -> List[Dict[str, Any]]:
        """Return a queue of mistakes ordered by wrong count."""
        if not self.engine:
            return []

        base_query = """
            SELECT game_mode, item_key, item_display, item_type, wrong_count, correct_count, context
            FROM mistake_items
            WHERE wrong_count > 0
        """
        if game_mode:
            base_query += " AND game_mode = :game_mode"
        base_query += " ORDER BY wrong_count DESC, correct_count ASC LIMIT :limit"
        query = text(base_query)
        try:
            with self.engine.begin() as conn:
                params = {"limit": limit}
                if game_mode:
                    params["game_mode"] = game_mode
                rows = conn.execute(query, params).mappings().all()
                results = []
                for row in rows:
                    item = dict(row)
                    context = item.get("context")
                    if isinstance(context, str):
                        item["context"] = json.loads(context)
                    results.append(item)
                return results
        except SQLAlchemyError as exc:
            logger.warning("Failed to load review items: %s", exc)
            return []
