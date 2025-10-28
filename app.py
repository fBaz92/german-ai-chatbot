"""
Streamlit Web Interface for German Translation Game
"""
import streamlit as st
from src.ai.datapizza_api import DatapizzaAPI
from src.functionalities.translation_game import TranslationGameFunctionality
from src.functionalities.inverse_translation_game import InverseTranslationGameFunctionality
from src.functionalities.word_selection_game import WordSelectionGameFunctionality
from src.functionalities.article_selection_game import ArticleSelectionGameFunctionality
from src.functionalities.fill_blank_game import FillBlankGameFunctionality
from src.functionalities.error_detection_game import ErrorDetectionGameFunctionality

# Page config
st.set_page_config(
    page_title="German Learning Games",
    page_icon="🇩🇪",
    layout="wide",
    initial_sidebar_state="expanded"
)

# Initialize session state
if 'api' not in st.session_state:
    st.session_state.api = None
if 'game' not in st.session_state:
    st.session_state.game = None
if 'current_sentence' not in st.session_state:
    st.session_state.current_sentence = None
if 'waiting_for_answer' not in st.session_state:
    st.session_state.waiting_for_answer = False
if 'feedback' not in st.session_state:
    st.session_state.feedback = None
if 'user_input' not in st.session_state:
    st.session_state.user_input = ""
if 'game_mode' not in st.session_state:
    st.session_state.game_mode = "German → English"
if 'hint_message' not in st.session_state:
    st.session_state.hint_message = None
if 'available_words' not in st.session_state:
    st.session_state.available_words = []
if 'selected_words' not in st.session_state:
    st.session_state.selected_words = []
if 'available_articles' not in st.session_state:
    st.session_state.available_articles = []
if 'case_info' not in st.session_state:
    st.session_state.case_info = None

def initialize_game(min_diff:int, max_diff:int, tense:str, provider:str, model:str, game_mode:str) -> bool:
    """
    Initialize the game with settings.
    
    Args:
        min_diff: Minimum difficulty level
        max_diff: Maximum difficulty level
        tense: Verb tense to practice
        provider: AI provider
        model: AI model
        game_mode: Game mode

    Returns:
        True if game initialized successfully, False otherwise
    """
    try:
        if "Google Gemini" in provider:  # Matches "Google Gemini (Cloud)"
            api = DatapizzaAPI(
                provider="google",
                model=model
            )
        else:  # Ollama
            api = DatapizzaAPI(
                provider="ollama",
                base_url="http://localhost:11434/v1",
                model=model
            )
        
        # Choose game type based on mode
        if game_mode == "English → German":
            game = InverseTranslationGameFunctionality(api=api)
            game.start_game(difficulty=(min_diff, max_diff), tense=tense)
        elif game_mode == "Word Selection (EN → DE)":
            game = WordSelectionGameFunctionality(api=api)
            game.start_game(difficulty=(min_diff, max_diff), tense=tense)
        elif game_mode == "Article Selection (der/die/das)":
            game = ArticleSelectionGameFunctionality(api=api)
            game.start_game(difficulty=(min_diff, max_diff))
        elif game_mode == "Fill-in-the-Blank":
            game = FillBlankGameFunctionality(api=api)
            game.start_game(difficulty=(min_diff, max_diff), tense=tense)
        elif game_mode == "Error Detection":
            game = ErrorDetectionGameFunctionality(api=api)
            game.start_game(difficulty=(min_diff, max_diff), tense=tense)
        else:  # German → English
            game = TranslationGameFunctionality(api=api)
            game.start_game(difficulty=(min_diff, max_diff), tense=tense)
        
        st.session_state.api = api
        st.session_state.game = game
        st.session_state.waiting_for_answer = False
        st.session_state.feedback = None
        
        return True
    except Exception as e:
        st.error(f"Error initializing game: {e}")
        return False

def get_next_sentence() -> bool:
    """Get next sentence/exercise from game.

    Returns:
        True if next exercise fetched successfully, False otherwise
    """
    if st.session_state.game:
        # Article Selection and Fill Blank use next_exercise() instead of next_sentence()
        if st.session_state.game_mode in ["Article Selection (der/die/das)", "Fill-in-the-Blank", "Error Detection"]:
            result = st.session_state.game.next_exercise()
        else:
            result = st.session_state.game.next_sentence()

        if result.get('success'):
            # Handle different game types
            if st.session_state.game_mode == "Word Selection (EN → DE)":
                st.session_state.current_sentence = result['english_sentence']
                st.session_state.available_words = result['all_words']
                st.session_state.selected_words = []
            elif st.session_state.game_mode == "Article Selection (der/die/das)":
                st.session_state.current_sentence = result['noun']
                st.session_state.available_articles = result['articles']
                st.session_state.case_info = result.get('case')
            else:
                st.session_state.current_sentence = result.get('sentence')

            st.session_state.waiting_for_answer = True
            st.session_state.feedback = None
            st.session_state.user_input = ""
            st.session_state.hint_message = None  # Reset hints
            return True
        else:
            st.error(result.get('error'))
            return False
    return False

def get_hint() -> bool:
    """Get a hint for current sentence.
    
    Returns:
        True if hint retrieved successfully, False otherwise
    """
    if st.session_state.game:
        result = st.session_state.game.get_hint()
        if result.get('success'):
            st.session_state.hint_message = result['message']
            return True
    return False

def check_answer(user_translation: str) -> bool:
    """Check user's translation.

    Args:
        user_translation: User's translation

    Returns:
        True if translation is correct, False otherwise
    """
    if st.session_state.game and user_translation.strip():
        result = st.session_state.game.check_translation(user_translation)
        st.session_state.feedback = result
        st.session_state.waiting_for_answer = False
        return result.get('is_correct', False)
    return False

def check_word_selection() -> bool:
    """Check user's word selection for word selection game.

    Returns:
        True if word selection is correct, False otherwise
    """
    if st.session_state.game and st.session_state.selected_words:
        result = st.session_state.game.check_word_selection(st.session_state.selected_words)
        st.session_state.feedback = result
        st.session_state.waiting_for_answer = False
        return result.get('is_correct', False)
    return False

def check_article_selection(selected_article: str) -> bool:
    """Check user's article selection for article selection game.

    Args:
        selected_article: Article selected by user

    Returns:
        True if article selection is correct, False otherwise
    """
    if st.session_state.game and selected_article:
        result = st.session_state.game.check_article_selection(selected_article)
        st.session_state.feedback = result
        st.session_state.waiting_for_answer = False
        return result.get('is_correct', False)
    return False

# Main UI
st.title("🇩🇪 German Learning Games")
st.markdown("Master German with 6 interactive game modes!")

# Sidebar - Settings
with st.sidebar:
    st.header("⚙️ Game Settings")

    # Game Mode
    st.subheader("🎮 Select Game Mode")
    game_mode = st.selectbox(
        "Choose a game",
        [
            "--- Translation Games ---",
            "German → English",
            "English → German",
            "--- Interactive Games ---",
            "Word Selection (EN → DE)",
            "Article Selection (der/die/das)",
            "Fill-in-the-Blank",
            "Error Detection"
        ],
        key="game_mode_selector"
    )

    # Filter out section headers
    if game_mode.startswith("---"):
        st.warning("Please select a game mode from the list")
        game_mode = None
    
    # Difficulty
    st.subheader("Difficulty Level")
    min_difficulty = st.slider("Minimum", 1, 5, 1, key="min_diff")
    max_difficulty = st.slider("Maximum", 1, 5, 3, key="max_diff")
    
    if min_difficulty > max_difficulty:
        st.warning("Min should be ≤ Max")
    
    # Tense (only for games that use it)
    if game_mode and game_mode not in ["Article Selection (der/die/das)"]:
        st.subheader("⏰ Verb Tense")
        tense = st.selectbox(
            "Select tense",
            ["Präsens", "Präteritum", "Perfekt", "Konjunktiv II", "Futur"],
            key="tense"
        )
    else:
        tense = "Präsens"  # Default for games that don't use tense
    
    # Provider
    st.subheader("AI Provider")
    provider = st.radio(
        "Choose provider",
        ["Ollama (Local)", "Google Gemini (Cloud)"],
        key="provider"
    )
    
    # Model
    st.subheader("AI Model")
    if provider == "Google Gemini (Cloud)":
        model = st.selectbox(
            "Google model",
            ["gemini-2.5-flash", "gemini-2.0-flash", "gemini-2.0-flash-lite"],
            key="model"
        )
    else:
        model = st.selectbox(
            "Ollama model",
            ["gemma3:4b", "gemma3:12b", "deepseek-r1:8b", "llama3.2"],
            key="model"
        )
    
    st.markdown("---")
    
    # Start/Reset button
    if st.button("🎮 Start New Game", use_container_width=True):
        if initialize_game(min_difficulty, max_difficulty, tense, provider, model, game_mode):
            st.session_state.game_mode = game_mode
            get_next_sentence()
            st.rerun()
    
    # Score display
    if st.session_state.game:
        st.markdown("---")
        st.subheader("📊 Score")
        score = st.session_state.game.score
        attempts = st.session_state.game.attempts
        if attempts > 0:
            percentage = int(score / attempts * 100)
            st.metric("Accuracy", f"{percentage}%")
            st.text(f"Correct: {score}/{attempts}")
        else:
            st.info("No attempts yet")
        
        # Show active configuration
        st.markdown("---")
        st.subheader("🤖 Active Config")
        if hasattr(st.session_state.api, 'provider'):
            st.text(f"Provider: {st.session_state.api.provider}")
            st.code(st.session_state.api.model)
        else:
            st.warning("Old session. Click 'Start New Game' to use new settings.")

# Main area
if st.session_state.game is None:
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

    ### 📝 How to Start:
    1. Select a game mode from the dropdown above
    2. Set your difficulty level (1=easiest, 5=hardest)
    3. Choose a verb tense (if applicable)
    4. Click 'Start New Game'
    5. Practice and get immediate AI feedback!

    **Tips:**
    - Start with difficulty 1-2 if you're a beginner
    - Article Selection is great for mastering der/die/das
    - Use hints if you get stuck (💡 button)
    - Track your progress in the sidebar!
    """)

elif st.session_state.current_sentence:
    # Display exercise with appropriate title based on game mode
    if st.session_state.game_mode == "Article Selection (der/die/das)":
        st.markdown("### Choose the correct article:")
    elif st.session_state.game_mode == "Fill-in-the-Blank":
        st.markdown("### Fill in the blank:")
    elif st.session_state.game_mode == "Error Detection":
        st.markdown("### Find and correct the error:")
    else:
        st.markdown("### Translate this sentence:")

    # Show appropriate flag/text based on game mode
    if st.session_state.game_mode == "English → German":
        st.markdown(f"## 🇬🇧 {st.session_state.current_sentence}")
    elif st.session_state.game_mode == "Word Selection (EN → DE)":
        st.markdown(f"## 🇬🇧 {st.session_state.current_sentence}")
    elif st.session_state.game_mode in ["Fill-in-the-Blank", "Error Detection"]:
        st.markdown(f"## 🇩🇪 {st.session_state.current_sentence}")
    elif st.session_state.game_mode == "Article Selection (der/die/das)":
        # Don't show the noun here, it's shown in the article selection UI
        pass
    else:
        st.markdown(f"## 🇩🇪 {st.session_state.current_sentence}")

    # Word Selection Game UI
    if st.session_state.game_mode == "Word Selection (EN → DE)" and st.session_state.waiting_for_answer:
        # Show hint if available
        if st.session_state.hint_message:
            st.info(st.session_state.hint_message)

        # Hint button
        if st.button("💡 Get Hint", use_container_width=True):
            get_hint()
            st.rerun()

        st.markdown("---")
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
                is_correct = check_word_selection()
                st.rerun()

    # Article Selection Game UI
    elif st.session_state.game_mode == "Article Selection (der/die/das)" and st.session_state.waiting_for_answer:
        # Show hint if available
        if st.session_state.hint_message:
            st.info(st.session_state.hint_message)

        # Hint button
        if st.button("💡 Get Hint", use_container_width=True, key="article_hint_btn"):
            get_hint()
            st.rerun()

        st.markdown("---")

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

        # Display articles as large buttons in a row
        cols = st.columns(len(st.session_state.available_articles))
        for idx, article in enumerate(st.session_state.available_articles):
            with cols[idx]:
                if st.button(article, key=f"article_{idx}", use_container_width=True, type="primary"):
                    is_correct = check_article_selection(article)
                    st.rerun()

    # Input area for text-based games
    elif st.session_state.waiting_for_answer and st.session_state.game_mode not in ["Word Selection (EN → DE)", "Article Selection (der/die/das)"]:
        # Show hint if available
        if st.session_state.hint_message:
            st.info(st.session_state.hint_message)
        
        # Hint button
        if st.button("💡 Get Hint", use_container_width=True):
            get_hint()
            st.rerun()
        
        st.markdown("---")
        
        # Show input form
        with st.form(key="translation_form", clear_on_submit=True):
            # Set labels and placeholders based on game mode
            if st.session_state.game_mode == "English → German":
                label = "Your German translation:"
                placeholder = "Schreibe deine Übersetzung hier..."
            elif st.session_state.game_mode == "Fill-in-the-Blank":
                label = "Fill in the blank:"
                placeholder = "Type the missing word..."
            elif st.session_state.game_mode == "Error Detection":
                label = "Type the corrected sentence:"
                placeholder = "Schreibe den korrigierten Satz..."
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
                is_correct = check_answer(user_translation)
                st.rerun()
    
    # Show feedback
    if st.session_state.feedback:
        result = st.session_state.feedback
        
        if result.get('is_correct'):
            st.success("✅ " + result['message'])
            
            # Auto-advance button
            col1, col2 = st.columns([3, 1])
            with col1:
                if st.button("➡️ Next Sentence", use_container_width=True, type="primary"):
                    get_next_sentence()
                    st.rerun()
            with col2:
                if st.button("⏸️ Stop", use_container_width=True):
                    st.session_state.game = None
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
                    get_next_sentence()
                    st.rerun()

else:
    # Game initialized but no sentence yet
    if st.button("🎯 Get First Sentence"):
        get_next_sentence()
        st.rerun()

# Footer
st.markdown("---")