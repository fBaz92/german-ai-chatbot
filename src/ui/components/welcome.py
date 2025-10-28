"""
Welcome screen component.
Displays initial instructions when no game is active.
"""
import streamlit as st


def render_welcome():
    """Render the welcome screen with instructions."""
    st.info("👈 Configure settings and click 'Start New Game' to begin!")
    st.markdown("""
    ### 🎮 Available Game Modes:

    **Translation Games:**
    - **German → English**: Type English translations of German sentences
    - **English → German**: Type German translations of English sentences

    **Interactive Games:**
    - **Word Selection**: Build German sentences by selecting words in order
    - **Article Selection**: Choose the correct article (der/die/das) with different cases
    - **Fill-in-the-Blank**: Complete German sentences with missing words
    - **Error Detection**: Find and correct errors in German sentences
    - **Verb Conjugation Challenge**: Practice conjugating German verbs with different pronouns and tenses

    **Advanced Games:**
    - **Speed Translation Race**: Translate words and phrases quickly for bonus points and combos!
    - **Conversation Builder**: Navigate realistic scenarios by choosing appropriate German responses

    ### 📝 How to Start:
    1. Select a game mode from the dropdown above
    2. Set your difficulty level (1=easiest, 5=hardest)
    3. Choose a verb tense (if applicable)
    4. Click 'Start New Game'
    5. Practice and get immediate AI feedback!

    **Tips:**
    - Start with difficulty 1-2 if you're a beginner
    - Article Selection is great for mastering der/die/das
    - Verb Conjugation builds muscle memory for verb forms
    - Speed Translation Race tests your fluency under pressure
    - Conversation Builder prepares you for real-world scenarios
    - Use hints if you get stuck (💡 button)
    - Track your progress in the sidebar!
    """)
