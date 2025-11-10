"""Static configuration shared with the web front-end."""

GAME_OPTIONS = [
    {"label": "German → English", "value": "German → English", "category": "Translation"},
    {"label": "English → German", "value": "English → German", "category": "Translation"},
    {"label": "Word Selection (EN → DE)", "value": "Word Selection (EN → DE)", "category": "Interactive"},
    {"label": "Article Selection (der/die/das)", "value": "Article Selection (der/die/das)", "category": "Interactive"},
    {"label": "Fill-in-the-Blank", "value": "Fill-in-the-Blank", "category": "Interactive"},
    {"label": "Error Detection", "value": "Error Detection", "category": "Interactive"},
    {"label": "Verb Conjugation Challenge", "value": "Verb Conjugation Challenge", "category": "Interactive"},
    {"label": "Speed Translation Race", "value": "Speed Translation Race", "category": "Advanced"},
    {"label": "Conversation Builder", "value": "Conversation Builder", "category": "Advanced"},
]

TENSE_OPTIONS = [
    "Präsens",
    "Präteritum",
    "Perfekt",
    "Konjunktiv II",
    "Futur",
]

PROVIDERS = [
    {
        "label": "Ollama (Local)",
        "value": "ollama",
        "models": ["gemma3:4b", "gemma3:12b", "deepseek-r1:8b", "llama3.2"],
    },
    {
        "label": "Google Gemini (Cloud)",
        "value": "google",
        "models": ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite"],
    },
]
