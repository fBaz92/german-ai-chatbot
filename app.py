"""Flask entrypoint for the German AI Chatbot."""
from __future__ import annotations

import os

from src.web import create_app

app = create_app()


if __name__ == "__main__":
    port = int(os.getenv("PORT", 8000))
    app.run(host="0.0.0.0", port=port, debug=os.getenv("FLASK_DEBUG") == "1")
