"""
Word Selection Game UI.
Interactive interface for building German sentences by selecting words in order.
"""
import streamlit as st
from src.ui.games.base_game_ui import BaseGameUI


class WordSelectionUI(BaseGameUI):
    """UI for Word Selection game (EN → DE)."""

    def render_exercise_display(self):
        """Render the word selection exercise."""
        st.markdown("### Translate this sentence:")
        st.markdown(f"## 🇬🇧 {st.session_state.current_sentence}")

    def render_input_area(self):
        """Render word selection interface."""
        st.markdown("### Select words in order to build the German translation:")

        # Display selected words
        if st.session_state.selected_words:
            st.markdown("**Your answer:**")
            selected_text = " ".join(st.session_state.selected_words)
            st.markdown(f"### 🇩🇪 {selected_text}")

            # Remove last word button
            col1, col2 = st.columns([1, 1])
            with col1:
                if st.button("⬅️ Remove Last Word", use_container_width=True):
                    if st.session_state.selected_words:
                        st.session_state.selected_words.pop()
                        st.rerun()
            with col2:
                if st.button("🔄 Reset", use_container_width=True):
                    st.session_state.selected_words = []
                    st.rerun()
        else:
            st.info("👆 Click words below to build your answer")

        st.markdown("---")
        st.markdown("**Available words:**")

        # Display available words as buttons in a grid
        # Create rows of buttons (5 words per row)
        words_per_row = 5
        available_words = st.session_state.available_words

        for i in range(0, len(available_words), words_per_row):
            cols = st.columns(words_per_row)
            for j, col in enumerate(cols):
                if i + j < len(available_words):
                    word = available_words[i + j]
                    with col:
                        # Disable if already selected
                        if word in st.session_state.selected_words:
                            st.button(word, disabled=True, key=f"word_{i}_{j}", use_container_width=True)
                        else:
                            if st.button(word, key=f"word_{i}_{j}", use_container_width=True):
                                st.session_state.selected_words.append(word)
                                st.rerun()

        st.markdown("---")

        # Submit button
        if st.session_state.selected_words:
            if st.button("✅ Check Answer", use_container_width=True, type="primary"):
                is_correct = self.state_manager.check_word_selection()
                st.rerun()
