"""
Error Detection Game UI.
Interface for finding and correcting errors in German sentences.
"""
import streamlit as st
from src.ui.games.base_game_ui import BaseGameUI


class ErrorDetectionUI(BaseGameUI):
    """UI for Error Detection game."""

    def render_exercise_display(self):
        """Render the error detection exercise."""
        st.markdown("### Find and correct the error:")
        st.markdown(f"## 🇩🇪 {st.session_state.current_sentence}")

    def render_input_area(self):
        """Render error correction text input."""
        # Show input form
        with st.form(key="error_detection_form", clear_on_submit=True):
            user_translation = st.text_input(
                "Type the corrected sentence:",
                key="input_field",
                placeholder="Schreibe den korrigierten Satz..."
            )
            submit = st.form_submit_button("✅ Check Answer", use_container_width=True)

            if submit and user_translation:
                self.state_manager.check_answer(user_translation)
                st.rerun()
