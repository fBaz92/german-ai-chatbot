"""
Translation Games UI.
Text input interface for German ↔ English translation games.
"""
import streamlit as st
from src.ui.games.base_game_ui import BaseGameUI


class TranslationUI(BaseGameUI):
    """UI for translation games (German → English and English → German)."""

    def render_exercise_display(self):
        """Render the translation exercise."""
        st.markdown("### Translate this sentence:")

        # Show appropriate flag/text based on game mode
        if st.session_state.game_mode == "English → German":
            st.markdown(f"## 🇬🇧 {st.session_state.current_sentence}")
        else:  # German → English
            st.markdown(f"## 🇩🇪 {st.session_state.current_sentence}")

    def render_input_area(self):
        """Render translation text input."""
        # Show input form
        with st.form(key="translation_form", clear_on_submit=True):
            # Set labels and placeholders based on game mode
            if st.session_state.game_mode == "English → German":
                label = "Your German translation:"
                placeholder = "Schreibe deine Übersetzung hier..."
            else:  # German → English
                label = "Your English translation:"
                placeholder = "Type your translation here..."

            user_translation = st.text_input(
                label,
                key="input_field",
                placeholder=placeholder
            )
            submit = st.form_submit_button("✅ Check Answer", use_container_width=True)

            if submit and user_translation:
                self.state_manager.check_answer(user_translation)
                st.rerun()
