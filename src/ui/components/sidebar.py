"""
Sidebar component for game settings.
"""
import streamlit as st
from dataclasses import dataclass
from typing import Optional


@dataclass
class GameSettings:
    """Settings returned from sidebar."""
    game_mode: Optional[str]
    min_difficulty: int
    max_difficulty: int
    tense: str
    provider: str
    model: str
    start_new_game: bool = False


def render_sidebar(game: Optional[object] = None, api: Optional[object] = None) -> GameSettings:
    """
    Render sidebar and return game settings.

    Args:
        game: Current game instance for score display
        api: Current API instance for config display

    Returns:
        GameSettings object with user selections
    """
    with st.sidebar:
        st.header("⚙️ Game Settings")

        # Game Mode
        st.subheader("🎮 Select Game Mode")
        game_mode = st.selectbox(
            "Choose a game",
            [
                "--- Translation Games ---",
                "German → English",
                "English → German",
                "--- Interactive Games ---",
                "Word Selection (EN → DE)",
                "Article Selection (der/die/das)",
                "Fill-in-the-Blank",
                "Error Detection"
            ],
            key="game_mode_selector"
        )

        # Filter out section headers
        if game_mode.startswith("---"):
            st.warning("Please select a game mode from the list")
            game_mode = None

        # Difficulty
        st.subheader("Difficulty Level")
        min_difficulty = st.slider("Minimum", 1, 5, 1, key="min_diff")
        max_difficulty = st.slider("Maximum", 1, 5, 3, key="max_diff")

        if min_difficulty > max_difficulty:
            st.warning("Min should be ≤ Max")

        # Tense (only for games that use it)
        if game_mode and game_mode not in ["Article Selection (der/die/das)"]:
            st.subheader("⏰ Verb Tense")
            tense = st.selectbox(
                "Select tense",
                ["Präsens", "Präteritum", "Perfekt", "Konjunktiv II", "Futur"],
                key="tense"
            )
        else:
            tense = "Präsens"  # Default for games that don't use tense

        # Provider
        st.subheader("AI Provider")
        provider = st.radio(
            "Choose provider",
            ["Ollama (Local)", "Google Gemini (Cloud)"],
            key="provider"
        )

        # Model
        st.subheader("AI Model")
        if provider == "Google Gemini (Cloud)":
            model = st.selectbox(
                "Google model",
                ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite"],
                key="model"
            )
        else:
            model = st.selectbox(
                "Ollama model",
                ["gemma3:4b", "gemma3:12b", "deepseek-r1:8b", "llama3.2"],
                key="model"
            )

        st.markdown("---")

        # Start/Reset button
        start_new_game = st.button("🎮 Start New Game", use_container_width=True)

        # Score display
        if game:
            st.markdown("---")
            st.subheader("📊 Score")
            score = game.score
            attempts = game.attempts
            if attempts > 0:
                percentage = int(score / attempts * 100)
                st.metric("Accuracy", f"{percentage}%")
                st.text(f"Correct: {score}/{attempts}")
            else:
                st.info("No attempts yet")

            # Show active configuration
            st.markdown("---")
            st.subheader("🤖 Active Config")
            if api and hasattr(api, 'provider'):
                st.text(f"Provider: {api.provider}")
                st.code(api.model)
            else:
                st.warning("Old session. Click 'Start New Game' to use new settings.")

        return GameSettings(
            game_mode=game_mode,
            min_difficulty=min_difficulty,
            max_difficulty=max_difficulty,
            tense=tense,
            provider=provider,
            model=model,
            start_new_game=start_new_game
        )
