"""
Speed Translation Game UI.
Interface for timed German to English translations.
"""
import streamlit as st
import time
from src.ui.games.base_game_ui import BaseGameUI


class SpeedTranslationUI(BaseGameUI):
    """UI for Speed Translation game."""

    def render_exercise_display(self):
        """Render the speed translation exercise with timer."""
        st.markdown("### Translate quickly!")

        # Show current phrase with emphasis
        st.markdown(f"## 🇩🇪 **{st.session_state.current_sentence}**")

        # Show timer if we have start time in session state
        if hasattr(st.session_state.game, 'start_time') and hasattr(st.session_state.game, 'time_limit'):
            game = st.session_state.game
            time_elapsed = time.time() - game.start_time
            time_remaining = max(0, game.time_limit - time_elapsed)

            # Color code the timer
            if time_remaining > game.time_limit * 0.5:
                timer_color = "🟢"
            elif time_remaining > game.time_limit * 0.25:
                timer_color = "🟡"
            else:
                timer_color = "🔴"

            # Show timer and combo
            col1, col2 = st.columns(2)
            with col1:
                st.metric("⏱️ Time Remaining", f"{timer_color} {time_remaining:.1f}s")
            with col2:
                combo_emoji = "🔥" if game.combo > 0 else "💤"
                st.metric(f"{combo_emoji} Combo", f"{game.combo}x")

    def render_input_area(self):
        """Render speed translation text input."""
        # Show input form
        with st.form(key="speed_translation_form", clear_on_submit=True):
            user_translation = st.text_input(
                "Your English translation:",
                key="input_field",
                placeholder="Type quickly...",
                label_visibility="collapsed"
            )
            submit = st.form_submit_button("✅ Submit", use_container_width=True, type="primary")

            if submit and user_translation:
                self.state_manager.check_answer(user_translation)
                st.rerun()

        # Add skip button outside form
        if st.button("⏭️ Skip (Break Combo)", use_container_width=True):
            if hasattr(st.session_state.game, 'combo'):
                st.session_state.game.combo = 0
            self.state_manager.get_next_exercise()
            st.rerun()
