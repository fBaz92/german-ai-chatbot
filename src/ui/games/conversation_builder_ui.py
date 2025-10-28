"""
Conversation Builder Game UI.
Interface for multi-turn conversation scenarios with choice selection.
"""
import streamlit as st
from src.ui.games.base_game_ui import BaseGameUI


class ConversationBuilderUI(BaseGameUI):
    """UI for Conversation Builder game."""

    def render_exercise_display(self):
        """Render the conversation scenario and history."""
        # Show scenario description
        st.markdown("### 🗣️ Conversation Scenario")
        st.info(st.session_state.current_sentence)

        # Get current turn info from game
        if st.session_state.game:
            turn_info = st.session_state.game.get_current_turn()

            if turn_info.get("completed"):
                st.success("✅ Conversation completed!")
                return

            # Show conversation history
            if turn_info.get("history"):
                st.markdown("---")
                st.markdown("### 💬 Conversation History")

                for entry in turn_info["history"]:
                    if entry["speaker"] == "ai":
                        with st.chat_message("assistant"):
                            st.markdown(f"🇩🇪 **{entry['text']}**")
                            st.caption(f"🇬🇧 {entry['translation']}")
                    else:
                        icon = "✅" if entry.get("correct") else "❌"
                        with st.chat_message("user"):
                            st.markdown(f"{icon} 🇩🇪 **{entry['text']}**")

                st.markdown("---")

            # Show current turn
            turn = turn_info.get("turn")
            if turn:
                # If it's an AI turn, show it and auto-advance
                if turn.speaker == "ai":
                    with st.chat_message("assistant"):
                        st.markdown(f"🇩🇪 **{turn.german_text}**")
                        st.caption(f"🇬🇧 {turn.english_translation}")

                    # Auto-advance AI turn
                    if st.session_state.waiting_for_answer:
                        st.session_state.game.advance_ai_turn()
                        st.session_state.waiting_for_answer = True
                        st.rerun()

                # If it's a user turn, show the prompt
                elif turn.speaker == "user":
                    st.markdown("### Your turn to respond:")
                    progress = f"{turn_info['turn_index'] + 1}/{turn_info['total_turns']}"
                    st.progress((turn_info['turn_index'] + 1) / turn_info['total_turns'],
                               text=f"Turn {progress}")

    def render_input_area(self):
        """Render response option buttons for user turn."""
        if not st.session_state.game:
            return

        turn_info = st.session_state.game.get_current_turn()

        if turn_info.get("completed"):
            # Show final score and restart option
            col1, col2 = st.columns(2)
            with col1:
                if st.button("🎯 New Conversation", use_container_width=True, type="primary"):
                    self.state_manager.get_next_exercise()
                    st.rerun()
            with col2:
                if st.button("⏸️ Stop", use_container_width=True):
                    self.state_manager.reset_game()
                    st.rerun()
            return

        turn = turn_info.get("turn")

        if turn and turn.speaker == "user":
            st.markdown("**Choose your response:**")

            # Display response options as buttons
            for idx, option in enumerate(turn.options):
                if st.button(
                    f"**{chr(65 + idx)})** {option}",
                    key=f"conv_option_{idx}",
                    use_container_width=True
                ):
                    # Select this response
                    result = st.session_state.game.select_response(idx)
                    st.session_state.feedback = result

                    # Check if conversation is complete
                    if result.get("conversation_complete"):
                        st.session_state.waiting_for_answer = False
                    else:
                        # Auto-advance to next turn after showing feedback
                        st.session_state.waiting_for_answer = True

                    st.rerun()

    def render_feedback(self):
        """Override feedback to handle conversation completion."""
        if st.session_state.feedback:
            result = st.session_state.feedback

            if result.get('is_correct'):
                st.success("✅ " + result['message'])
            else:
                st.warning("⚠️ " + result['message'])

            # Show continue button after feedback
            if not result.get("conversation_complete"):
                if st.button("➡️ Continue", use_container_width=True, type="primary"):
                    st.session_state.feedback = None

                    # Advance AI turns automatically
                    while st.session_state.game:
                        turn_info = st.session_state.game.get_current_turn()
                        if turn_info.get("completed"):
                            break

                        turn = turn_info.get("turn")
                        if turn and turn.speaker == "ai":
                            st.session_state.game.advance_ai_turn()
                        else:
                            break

                    st.rerun()
            else:
                # Conversation complete
                st.balloons()
                col1, col2 = st.columns(2)
                with col1:
                    if st.button("🎯 New Conversation", use_container_width=True, type="primary"):
                        st.session_state.feedback = None
                        self.state_manager.get_next_exercise()
                        st.rerun()
                with col2:
                    if st.button("⏸️ Stop", use_container_width=True):
                        self.state_manager.reset_game()
                        st.rerun()
