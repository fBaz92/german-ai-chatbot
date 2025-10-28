"""
Base class for game UIs.
Defines the interface that all game-specific UIs must implement.
"""
from abc import ABC, abstractmethod
import streamlit as st
from src.ui.state_manager import StateManager


class BaseGameUI(ABC):
    """
    Abstract base class for game UIs.
    Each game mode should implement this interface.
    """

    def __init__(self):
        """Initialize the game UI."""
        self.state_manager = StateManager()

    @abstractmethod
    def render_exercise_display(self):
        """
        Render the exercise/sentence display.
        This shows what the user needs to respond to.
        """
        pass

    @abstractmethod
    def render_input_area(self):
        """
        Render the input area where users provide their answer.
        This could be text input, buttons, selections, etc.
        """
        pass

    def render_hint_button(self):
        """
        Render the hint button (common across all games).
        Can be overridden if game needs custom hint behavior.
        """
        if st.session_state.hint_message:
            st.info(st.session_state.hint_message)

        if st.button("💡 Get Hint", use_container_width=True, key=f"hint_btn_{id(self)}"):
            self.state_manager.get_hint()
            st.rerun()

    def render_feedback(self):
        """
        Render feedback after user submits answer (common across all games).
        Can be overridden if game needs custom feedback display.
        """
        if st.session_state.feedback:
            result = st.session_state.feedback

            if result.get('is_correct'):
                st.success("✅ " + result['message'])

                # Auto-advance button
                col1, col2 = st.columns([3, 1])
                with col1:
                    if st.button("➡️ Next Sentence", use_container_width=True, type="primary"):
                        self.state_manager.get_next_exercise()
                        st.rerun()
                with col2:
                    if st.button("⏸️ Stop", use_container_width=True):
                        self.state_manager.reset_game()
                        st.rerun()
            else:
                st.error("❌ " + result['message'])

                # Try again or next
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🔄 Try Again", use_container_width=True):
                        st.session_state.waiting_for_answer = True
                        st.session_state.feedback = None
                        # Reset selected words for word selection game
                        if st.session_state.game_mode == "Word Selection (EN → DE)":
                            st.session_state.selected_words = []
                        st.rerun()
                with col2:
                    if st.button("➡️ Skip", use_container_width=True):
                        self.state_manager.get_next_exercise()
                        st.rerun()

    def render(self):
        """
        Main render method that orchestrates the full game UI.
        Calls the abstract methods in the correct order.
        """
        # Render exercise display
        self.render_exercise_display()

        # If waiting for answer, show input area
        if st.session_state.waiting_for_answer:
            self.render_hint_button()
            st.markdown("---")
            self.render_input_area()

        # Show feedback
        self.render_feedback()
