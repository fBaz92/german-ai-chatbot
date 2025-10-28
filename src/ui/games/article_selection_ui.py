"""
Article Selection Game UI.
Interactive interface for choosing correct German articles (der/die/das).
"""
import streamlit as st
from src.ui.games.base_game_ui import BaseGameUI


class ArticleSelectionUI(BaseGameUI):
    """UI for Article Selection game (der/die/das)."""

    def render_exercise_display(self):
        """Render the article selection exercise."""
        st.markdown("### Choose the correct article:")

        # Prominently display the case with color-coding
        if st.session_state.case_info:
            case_colors = {
                "Nominativ": "🟦",
                "Akkusativ": "🟩",
                "Dativ": "🟨",
                "Genitiv": "🟥"
            }
            case_icon = case_colors.get(st.session_state.case_info, "📘")
            st.info(f"### {case_icon} **Case: {st.session_state.case_info}** {case_icon}")

        st.markdown(f"### Select the correct article for: **{st.session_state.current_sentence}**")
        st.markdown("**Choose the correct article:**")

    def render_input_area(self):
        """Render article selection buttons."""
        # Display articles as large buttons in a row
        cols = st.columns(len(st.session_state.available_articles))
        for idx, article in enumerate(st.session_state.available_articles):
            with cols[idx]:
                if st.button(article, key=f"article_{idx}", use_container_width=True, type="primary"):
                    self.state_manager.check_article_selection(article)
                    st.rerun()
