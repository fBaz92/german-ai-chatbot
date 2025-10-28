"""
Fill-in-the-Blank Game UI.
Interface for completing German sentences with missing words.
"""
import streamlit as st
from src.ui.games.base_game_ui import BaseGameUI


class FillBlankUI(BaseGameUI):
    """UI for Fill-in-the-Blank game."""

    def render_exercise_display(self):
        """Render the fill-in-the-blank exercise."""
        st.markdown("### Fill in the blank:")
        st.markdown(f"## 🇩🇪 {st.session_state.current_sentence}")

    def render_input_area(self):
        """Render fill-in-the-blank text input."""
        # Show input form
        with st.form(key="fill_blank_form", clear_on_submit=True):
            user_translation = st.text_input(
                "Fill in the blank:",
                key="input_field",
                placeholder="Type the missing word..."
            )
            submit = st.form_submit_button("✅ Check Answer", use_container_width=True)

            if submit and user_translation:
                self.state_manager.check_answer(user_translation)
                st.rerun()
