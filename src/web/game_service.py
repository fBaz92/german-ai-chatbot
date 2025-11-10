"""Business logic that bridges Flask routes with game functionalities."""
from __future__ import annotations

from typing import Any, Dict, List, Optional

from src.ai.datapizza_api import DatapizzaAPI
from src.functionalities.article_selection_game import ArticleSelectionGameFunctionality
from src.functionalities.conversation_builder_game import ConversationBuilderGameFunctionality
from src.functionalities.error_detection_game import ErrorDetectionGameFunctionality
from src.functionalities.fill_blank_game import FillBlankGameFunctionality
from src.functionalities.inverse_translation_game import InverseTranslationGameFunctionality
from src.functionalities.speed_translation_game import SpeedTranslationGameFunctionality
from src.functionalities.translation_game import TranslationGameFunctionality
from src.functionalities.verb_conjugation_game import VerbConjugationGameFunctionality
from src.functionalities.word_selection_game import WordSelectionGameFunctionality
from src.web import config
from src.web.session_store import SessionData, SessionStore


GAME_CLASS_MAP = {
    "German → English": TranslationGameFunctionality,
    "English → German": InverseTranslationGameFunctionality,
    "Word Selection (EN → DE)": WordSelectionGameFunctionality,
    "Article Selection (der/die/das)": ArticleSelectionGameFunctionality,
    "Fill-in-the-Blank": FillBlankGameFunctionality,
    "Error Detection": ErrorDetectionGameFunctionality,
    "Verb Conjugation Challenge": VerbConjugationGameFunctionality,
    "Speed Translation Race": SpeedTranslationGameFunctionality,
    "Conversation Builder": ConversationBuilderGameFunctionality,
}

NEXT_EXERCISE_GAMES = {
    "Article Selection (der/die/das)",
    "Fill-in-the-Blank",
    "Error Detection",
    "Verb Conjugation Challenge",
    "Speed Translation Race",
    "Conversation Builder",
}

TENSe_NOT_REQUIRED = {
    "Article Selection (der/die/das)",
}

GAME_UI_TYPES = {
    "German → English": "translation",
    "English → German": "translation",
    "Word Selection (EN → DE)": "word-selection",
    "Article Selection (der/die/das)": "article-selection",
    "Fill-in-the-Blank": "fill-blank",
    "Error Detection": "error-detection",
    "Verb Conjugation Challenge": "verb-conjugation",
    "Speed Translation Race": "speed-translation",
    "Conversation Builder": "conversation",
}


class GameService:
    """Encapsulates orchestration between HTTP routes and game classes."""

    def __init__(self, session_store: SessionStore):
        self.session_store = session_store

    @staticmethod
    def get_ui_config() -> Dict[str, Any]:
        """Expose form configuration for the front-end."""
        return {
            "games": config.GAME_OPTIONS,
            "tenses": config.TENSE_OPTIONS,
            "providers": config.PROVIDERS,
            "difficulty": {"min": 1, "max": 5},
        }

    def start_game(self, session: SessionData, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Initialize a game and return the first exercise."""
        game_mode = payload.get("gameMode")
        if game_mode not in GAME_CLASS_MAP:
            return {"success": False, "error": "Unknown game mode."}

        provider = payload.get("provider")
        model = payload.get("model")
        min_diff = int(payload.get("minDifficulty", 1))
        max_diff = int(payload.get("maxDifficulty", 3))
        tense = payload.get("tense", "Präsens")

        try:
            api = self._build_api_client(provider, model)
        except Exception as exc:
            return {"success": False, "error": str(exc)}

        game_cls = GAME_CLASS_MAP[game_mode]
        game = game_cls(api=api)

        kwargs = {"difficulty": (min_diff, max_diff)}
        if game_mode not in TENSe_NOT_REQUIRED:
            kwargs["tense"] = tense

        start_result = game.start_game(**kwargs)
        if not start_result.get("success", False):
            return {"success": False, "error": start_result.get("error", "Could not start game.")}

        # Persist session state
        session.api = api
        session.game = game
        session.game_mode = game_mode
        session.waiting_for_answer = False
        session.feedback = None
        self.session_store.touch(session)

        return self.fetch_next(session)

    def fetch_next(self, session: SessionData) -> Dict[str, Any]:
        """Fetch the next exercise for the active game."""
        if not session.game:
            return {"success": False, "error": "No active game."}

        try:
            if session.game_mode in NEXT_EXERCISE_GAMES:
                result = session.game.next_exercise()
            else:
                result = session.game.next_sentence()
        except Exception as exc:
            return {"success": False, "error": f"Failed to get next exercise: {exc}"}

        if not result or not result.get("success"):
            return {"success": False, "error": result.get("error", "Unknown error.")}

        session.waiting_for_answer = True
        session.feedback = None
        self.session_store.touch(session)

        exercise = self._format_exercise_payload(session, result)
        return {"success": True, "exercise": exercise}

    def submit_answer(self, session: SessionData, payload: Dict[str, Any]) -> Dict[str, Any]:
        """Validate a user answer and return feedback."""
        if not session.game:
            return {"success": False, "error": "No active game."}

        game = session.game
        game_mode = session.game_mode
        answer_payload = payload or {}

        try:
            if game_mode == "Word Selection (EN → DE)":
                selected_words = answer_payload.get("selectedWords", [])
                result = game.check_word_selection(selected_words)
            elif game_mode == "Article Selection (der/die/das)":
                article = answer_payload.get("selectedArticle")
                result = game.check_article_selection(article)
            elif game_mode == "Conversation Builder":
                option_index = answer_payload.get("optionIndex")
                result = game.select_response(option_index)
            else:
                user_answer = answer_payload.get("answer", "")
                if hasattr(game, "check_translation"):
                    result = game.check_translation(user_answer)
                elif hasattr(game, "check_answer"):
                    result = game.check_answer(user_answer)
                else:
                    return {"success": False, "error": "This game does not support answer checks."}
        except Exception as exc:
            return {"success": False, "error": f"Failed to validate answer: {exc}"}

        session.waiting_for_answer = False
        session.feedback = result
        self.session_store.touch(session)

        response: Dict[str, Any] = {"success": True, "feedback": result}

        if game_mode == "Conversation Builder":
            response["conversation"] = self._build_conversation_payload(game)

        return response

    def get_hint(self, session: SessionData) -> Dict[str, Any]:
        """Return hint text if supported by the current game."""
        if not session.game or not hasattr(session.game, "get_hint"):
            return {"success": False, "error": "Hints are not available for this game."}

        try:
            result = session.game.get_hint()
        except Exception as exc:
            return {"success": False, "error": f"Failed to retrieve hint: {exc}"}

        if not result or not result.get("success"):
            return {"success": False, "error": result.get("error", "Unable to retrieve hint.")}

        session.feedback = result
        self.session_store.touch(session)
        return {"success": True, "hint": result.get("message")}

    def reset(self, session: SessionData) -> Dict[str, Any]:
        """Clear the active game from the session."""
        session.game = None
        session.api = None
        session.game_mode = None
        session.waiting_for_answer = False
        session.feedback = None
        self.session_store.touch(session)
        return {"success": True}

    def get_status(self, session: SessionData) -> Dict[str, Any]:
        """Return the current exercise (if any) and meta info."""
        if not session.game or not session.waiting_for_answer:
            return {"success": True, "exercise": None}

        # Attempt to rebuild payload from current game state
        if session.game_mode == "Conversation Builder":
            exercise = self._build_conversation_payload(session.game)
        else:
            exercise = self._format_exercise_payload(session, {})

        return {"success": True, "exercise": exercise}

    def _build_conversation_payload(self, game: ConversationBuilderGameFunctionality) -> Dict[str, Any]:
        """Build payload for conversation builder, auto advancing AI turns."""
        turn_info = game.get_current_turn()
        if not turn_info.get("success"):
            return {
                "type": "conversation",
                "completed": True,
                "history": turn_info.get("history", []),
            }

        # Auto advance AI turns so the user only sees actionable prompts
        while not turn_info.get("completed"):
            turn = turn_info.get("turn")
            if turn and turn.speaker == "ai":
                game.advance_ai_turn()
                turn_info = game.get_current_turn()
            else:
                break

        payload = {
            "type": "conversation",
            "completed": turn_info.get("completed", False),
            "history": turn_info.get("history", []),
            "learningFocus": getattr(game.conversation, "learning_focus", None) if getattr(game, "conversation", None) else None,
            "scenario": getattr(game.conversation, "scenario", None) if getattr(game, "conversation", None) else None,
            "scenarioDescription": getattr(game.conversation, "scenario_description", None) if getattr(game, "conversation", None) else None,
            "progress": {
                "current": turn_info.get("turn_index", 0) + 1,
                "total": turn_info.get("total_turns", 0),
            },
        }

        turn = turn_info.get("turn")
        if turn and not turn_info.get("completed"):
            payload["awaitingUser"] = turn.speaker == "user"
            payload["prompt"] = {
                "german": turn.german_text,
                "english": turn.english_translation,
                "options": turn.options,
            }
        else:
            payload["awaitingUser"] = False

        return payload

    def _format_exercise_payload(self, session: SessionData, result: Dict[str, Any]) -> Dict[str, Any]:
        """Normalize exercise payloads for the UI."""
        game_mode = session.game_mode
        exercise_type = GAME_UI_TYPES.get(game_mode, "translation")

        if exercise_type == "conversation":
            return self._build_conversation_payload(session.game)  # type: ignore[arg-type]

        if exercise_type == "translation":
            direction = "de-en" if game_mode == "German → English" else "en-de"
            sentence = result.get("sentence") or getattr(session.game, "current_sentence", "")
            return {
                "type": "translation",
                "direction": direction,
                "sentence": sentence,
                "verb": result.get("verb"),
                "tense": result.get("tense"),
            }

        if exercise_type == "word-selection":
            return {
                "type": "word-selection",
                "englishSentence": result.get("english_sentence")
                or getattr(session.game, "current_english_sentence", ""),
                "words": result.get("all_words") or getattr(session.game, "all_words", []),
            }

        if exercise_type == "article-selection":
            return {
                "type": "article-selection",
                "noun": result.get("noun") or getattr(session.game, "current_noun", ""),
                "case": result.get("case") or getattr(session.game, "case", ""),
                "articles": result.get("articles") or getattr(session.game, "all_articles", []),
                "meaning": result.get("meaning") or getattr(session.game, "meaning", ""),
                "exampleSentence": result.get("example_sentence") or getattr(session.game, "example_sentence", ""),
                "exampleTranslation": result.get("example_translation") or getattr(session.game, "example_translation", ""),
            }

        if exercise_type == "fill-blank":
            sentence = result.get("sentence") or getattr(session.game, "current_sentence", "")
            return {
                "type": "fill-blank",
                "sentence": sentence,
                "hint": result.get("hint") or getattr(session.game, "hint_text", ""),
            }

        if exercise_type == "error-detection":
            sentence = result.get("sentence") or getattr(session.game, "incorrect_sentence", "")
            return {
                "type": "error-detection",
                "sentence": sentence,
            }

        if exercise_type == "verb-conjugation":
            composed = result.get("sentence") or getattr(session.game, "current_sentence", "")
            pieces = composed.split(" + ")
            return {
                "type": "verb-conjugation",
                "infinitive": result.get("infinitive") or (pieces[0] if pieces else ""),
                "pronoun": result.get("pronoun") or (pieces[1] if len(pieces) > 1 else ""),
                "tense": result.get("tense") or (pieces[2] if len(pieces) > 2 else ""),
                "englishMeaning": result.get("english_meaning") or getattr(session.game, "english_meaning", ""),
            }

        if exercise_type == "speed-translation":
            return {
                "type": "speed-translation",
                "sentence": result.get("sentence") or getattr(session.game, "current_phrase", ""),
                "difficulty": result.get("difficulty") or getattr(session.game, "difficulty", ""),
                "category": result.get("category") or getattr(session.game, "category", ""),
                "timeLimit": result.get("time_limit") or getattr(session.game, "time_limit", ""),
            }

        return {"type": "unknown", "raw": result}

    @staticmethod
    def _build_api_client(provider: str, model: Optional[str]) -> DatapizzaAPI:
        """Create the DatapizzaAPI client based on provider settings."""
        provider = provider or "ollama"
        if provider not in {"ollama", "google"}:
            raise ValueError("Unsupported provider.")

        if provider == "google":
            return DatapizzaAPI(provider="google", model=model)

        # Default to local Ollama
        return DatapizzaAPI(provider="ollama", base_url="http://localhost:11434/v1", model=model)
