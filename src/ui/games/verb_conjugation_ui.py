"""
Verb Conjugation Game UI.
Interface for conjugating German verbs with pronoun + tense.
"""
import streamlit as st
from src.ui.games.base_game_ui import BaseGameUI


class VerbConjugationUI(BaseGameUI):
    """UI for Verb Conjugation game."""

    def render_exercise_display(self):
        """Render the verb conjugation exercise."""
        st.markdown("### Conjugate this verb:")

        # Display the exercise components in a nice format
        infinitive = st.session_state.current_sentence.split(" + ")[0]
        pronoun = st.session_state.current_sentence.split(" + ")[1] if " + " in st.session_state.current_sentence else ""
        tense = st.session_state.current_sentence.split(" + ")[2] if st.session_state.current_sentence.count(" + ") >= 2 else ""

        col1, col2, col3 = st.columns(3)
        with col1:
            st.info(f"**Verb:**\n\n{infinitive}")
        with col2:
            st.info(f"**Pronoun:**\n\n{pronoun}")
        with col3:
            st.info(f"**Tense:**\n\n{tense}")

    def render_input_area(self):
        """Render verb conjugation text input."""
        # Show input form
        with st.form(key="verb_conjugation_form", clear_on_submit=True):
            user_translation = st.text_input(
                "Your conjugated form:",
                key="input_field",
                placeholder="Type the conjugated verb..."
            )
            submit = st.form_submit_button("✅ Check Answer", use_container_width=True)

            if submit and user_translation:
                self.state_manager.check_answer(user_translation)
                st.rerun()
