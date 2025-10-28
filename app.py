"""
Streamlit Web Interface for German Learning Games.
Refactored to use component-based architecture.
"""
import streamlit as st
from src.ui.state_manager import StateManager
from src.ui.components.sidebar import render_sidebar
from src.ui.components.welcome import render_welcome
from src.ui.games import get_game_ui

# Page config
st.set_page_config(
    page_title="German Learning Games",
    page_icon="🇩🇪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize state manager
state_manager = StateManager()
state_manager.initialize_session_state()

# Main title
st.title("🇩🇪 German Learning Games")
st.markdown("Master German with 6 interactive game modes!")

# Render sidebar and get settings
settings = render_sidebar(
    game=st.session_state.game,
    api=st.session_state.api
)

# Handle game initialization
if settings.start_new_game and settings.game_mode:
    if state_manager.initialize_game(
        min_diff=settings.min_difficulty,
        max_diff=settings.max_difficulty,
        tense=settings.tense,
        provider=settings.provider,
        model=settings.model,
        game_mode=settings.game_mode
    ):
        st.session_state.game_mode = settings.game_mode
        state_manager.get_next_exercise()
        st.rerun()

# Main content area
if st.session_state.game is None:
    # Show welcome screen
    render_welcome()

elif st.session_state.current_sentence:
    # Render the appropriate game UI
    try:
        game_ui = get_game_ui(st.session_state.game_mode)
        game_ui.render()
    except ValueError as e:
        st.error(f"Error: {e}")

else:
    # Game initialized but no sentence yet
    if st.button("🎯 Get First Sentence"):
        state_manager.get_next_exercise()
        st.rerun()

# Footer
st.markdown("---")
