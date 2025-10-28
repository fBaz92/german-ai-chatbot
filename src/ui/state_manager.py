"""
Session state manager for Streamlit app.
Centralizes all session state initialization and management.
"""
import streamlit as st
from typing import Optional, Dict, Any
from src.ai.datapizza_api import DatapizzaAPI
from src.functionalities.translation_game import TranslationGameFunctionality
from src.functionalities.inverse_translation_game import InverseTranslationGameFunctionality
from src.functionalities.word_selection_game import WordSelectionGameFunctionality
from src.functionalities.article_selection_game import ArticleSelectionGameFunctionality
from src.functionalities.fill_blank_game import FillBlankGameFunctionality
from src.functionalities.error_detection_game import ErrorDetectionGameFunctionality


class StateManager:
    """Manages Streamlit session state for the German learning app."""

    @staticmethod
    def initialize_session_state():
        """Initialize all session state variables."""
        if 'api' not in st.session_state:
            st.session_state.api = None
        if 'game' not in st.session_state:
            st.session_state.game = None
        if 'current_sentence' not in st.session_state:
            st.session_state.current_sentence = None
        if 'waiting_for_answer' not in st.session_state:
            st.session_state.waiting_for_answer = False
        if 'feedback' not in st.session_state:
            st.session_state.feedback = None
        if 'user_input' not in st.session_state:
            st.session_state.user_input = ""
        if 'game_mode' not in st.session_state:
            st.session_state.game_mode = "German → English"
        if 'hint_message' not in st.session_state:
            st.session_state.hint_message = None
        if 'available_words' not in st.session_state:
            st.session_state.available_words = []
        if 'selected_words' not in st.session_state:
            st.session_state.selected_words = []
        if 'available_articles' not in st.session_state:
            st.session_state.available_articles = []
        if 'case_info' not in st.session_state:
            st.session_state.case_info = None

    @staticmethod
    def initialize_game(min_diff: int, max_diff: int, tense: str,
                       provider: str, model: str, game_mode: str) -> bool:
        """
        Initialize the game with settings.

        Args:
            min_diff: Minimum difficulty level
            max_diff: Maximum difficulty level
            tense: Verb tense to practice
            provider: AI provider
            model: AI model
            game_mode: Game mode

        Returns:
            True if game initialized successfully, False otherwise
        """
        try:
            if "Google Gemini" in provider:  # Matches "Google Gemini (Cloud)"
                api = DatapizzaAPI(
                    provider="google",
                    model=model
                )
            else:  # Ollama
                api = DatapizzaAPI(
                    provider="ollama",
                    base_url="http://localhost:11434/v1",
                    model=model
                )

            # Choose game type based on mode
            if game_mode == "English → German":
                game = InverseTranslationGameFunctionality(api=api)
                game.start_game(difficulty=(min_diff, max_diff), tense=tense)
            elif game_mode == "Word Selection (EN → DE)":
                game = WordSelectionGameFunctionality(api=api)
                game.start_game(difficulty=(min_diff, max_diff), tense=tense)
            elif game_mode == "Article Selection (der/die/das)":
                game = ArticleSelectionGameFunctionality(api=api)
                game.start_game(difficulty=(min_diff, max_diff))
            elif game_mode == "Fill-in-the-Blank":
                game = FillBlankGameFunctionality(api=api)
                game.start_game(difficulty=(min_diff, max_diff), tense=tense)
            elif game_mode == "Error Detection":
                game = ErrorDetectionGameFunctionality(api=api)
                game.start_game(difficulty=(min_diff, max_diff), tense=tense)
            else:  # German → English
                game = TranslationGameFunctionality(api=api)
                game.start_game(difficulty=(min_diff, max_diff), tense=tense)

            st.session_state.api = api
            st.session_state.game = game
            st.session_state.waiting_for_answer = False
            st.session_state.feedback = None

            return True
        except Exception as e:
            st.error(f"Error initializing game: {e}")
            return False

    @staticmethod
    def get_next_exercise() -> bool:
        """
        Get next sentence/exercise from game.

        Returns:
            True if next exercise fetched successfully, False otherwise
        """
        if st.session_state.game:
            # Article Selection, Fill Blank, and Error Detection use next_exercise()
            if st.session_state.game_mode in ["Article Selection (der/die/das)",
                                               "Fill-in-the-Blank", "Error Detection"]:
                result = st.session_state.game.next_exercise()
            else:
                result = st.session_state.game.next_sentence()

            if result.get('success'):
                # Handle different game types
                if st.session_state.game_mode == "Word Selection (EN → DE)":
                    st.session_state.current_sentence = result['english_sentence']
                    st.session_state.available_words = result['all_words']
                    st.session_state.selected_words = []
                elif st.session_state.game_mode == "Article Selection (der/die/das)":
                    st.session_state.current_sentence = result['noun']
                    st.session_state.available_articles = result['articles']
                    st.session_state.case_info = result.get('case')
                else:
                    st.session_state.current_sentence = result.get('sentence')

                st.session_state.waiting_for_answer = True
                st.session_state.feedback = None
                st.session_state.user_input = ""
                st.session_state.hint_message = None  # Reset hints
                return True
            else:
                st.error(result.get('error'))
                return False
        return False

    @staticmethod
    def get_hint() -> bool:
        """
        Get a hint for current sentence.

        Returns:
            True if hint retrieved successfully, False otherwise
        """
        if st.session_state.game:
            result = st.session_state.game.get_hint()
            if result.get('success'):
                st.session_state.hint_message = result['message']
                return True
        return False

    @staticmethod
    def check_answer(user_translation: str) -> bool:
        """
        Check user's translation.

        Args:
            user_translation: User's translation

        Returns:
            True if translation is correct, False otherwise
        """
        if st.session_state.game and user_translation.strip():
            result = st.session_state.game.check_translation(user_translation)
            st.session_state.feedback = result
            st.session_state.waiting_for_answer = False
            return result.get('is_correct', False)
        return False

    @staticmethod
    def check_word_selection() -> bool:
        """
        Check user's word selection for word selection game.

        Returns:
            True if word selection is correct, False otherwise
        """
        if st.session_state.game and st.session_state.selected_words:
            result = st.session_state.game.check_word_selection(st.session_state.selected_words)
            st.session_state.feedback = result
            st.session_state.waiting_for_answer = False
            return result.get('is_correct', False)
        return False

    @staticmethod
    def check_article_selection(selected_article: str) -> bool:
        """
        Check user's article selection for article selection game.

        Args:
            selected_article: Article selected by user

        Returns:
            True if article selection is correct, False otherwise
        """
        if st.session_state.game and selected_article:
            result = st.session_state.game.check_article_selection(selected_article)
            st.session_state.feedback = result
            st.session_state.waiting_for_answer = False
            return result.get('is_correct', False)
        return False

    @staticmethod
    def reset_game():
        """Reset the game state."""
        st.session_state.game = None
        st.session_state.current_sentence = None
        st.session_state.waiting_for_answer = False
        st.session_state.feedback = None
        st.session_state.hint_message = None
        st.session_state.selected_words = []

    # Properties for convenient access
    @property
    def game(self):
        """Get current game instance."""
        return st.session_state.get('game')

    @property
    def api(self):
        """Get current API instance."""
        return st.session_state.get('api')

    @property
    def game_mode(self) -> str:
        """Get current game mode."""
        return st.session_state.get('game_mode', "German → English")

    @property
    def current_sentence(self) -> Optional[str]:
        """Get current sentence/exercise."""
        return st.session_state.get('current_sentence')

    @property
    def waiting_for_answer(self) -> bool:
        """Check if waiting for user answer."""
        return st.session_state.get('waiting_for_answer', False)

    @property
    def feedback(self) -> Optional[Dict[str, Any]]:
        """Get current feedback."""
        return st.session_state.get('feedback')
