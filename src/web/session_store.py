"""In-memory session store for Flask front-end."""
from __future__ import annotations

import secrets
import threading
import time
from dataclasses import dataclass, field
from typing import Any, Dict, Optional, Tuple


SESSION_COOKIE_NAME = "german_ai_session"
DEFAULT_SESSION_TTL = 60 * 60 * 4  # 4 hours


@dataclass
class SessionData:
    """Represents the state we keep per browser session."""

    id: str
    game: Optional[Any] = None
    api: Optional[Any] = None
    game_mode: Optional[str] = None
    waiting_for_answer: bool = False
    feedback: Optional[Dict[str, Any]] = None
    pending_focus_item: Optional[Dict[str, Any]] = None
    review_queue: list = field(default_factory=list)
    review_active: bool = False
    created_at: float = field(default_factory=time.time)
    updated_at: float = field(default_factory=time.time)


class SessionStore:
    """Thread-safe in-memory session store with TTL cleanup."""

    def __init__(self, ttl: int = DEFAULT_SESSION_TTL):
        self.ttl = ttl
        self._sessions: Dict[str, SessionData] = {}
        self._lock = threading.Lock()

    def _purge_expired(self) -> None:
        """Remove expired sessions to free memory."""
        now = time.time()
        expired = [sid for sid, session in self._sessions.items() if now - session.updated_at > self.ttl]
        for sid in expired:
            self._sessions.pop(sid, None)

    def create_session(self) -> SessionData:
        """Create and store a new session."""
        session_id = secrets.token_hex(16)
        session = SessionData(id=session_id)
        with self._lock:
            self._purge_expired()
            self._sessions[session_id] = session
        return session

    def get_session(self, session_id: Optional[str]) -> Optional[SessionData]:
        """Retrieve an existing session if present and not expired."""
        if not session_id:
            return None

        with self._lock:
            session = self._sessions.get(session_id)
            if not session:
                return None
            if time.time() - session.updated_at > self.ttl:
                # Drop expired session
                self._sessions.pop(session_id, None)
                return None
            return session

    def get_or_create(self, session_id: Optional[str]) -> Tuple[SessionData, bool]:
        """Fetch an existing session or create a new one."""
        session = self.get_session(session_id)
        if session:
            return session, False
        return self.create_session(), True

    def touch(self, session: SessionData) -> None:
        """Update last-used timestamp."""
        session.updated_at = time.time()

    def clear_session(self, session_id: str) -> None:
        """Remove a session explicitly."""
        with self._lock:
            self._sessions.pop(session_id, None)
