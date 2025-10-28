"""
Game UI registry.
Factory for getting the appropriate UI for each game mode.
"""
from src.ui.games.translation_ui import TranslationUI
from src.ui.games.word_selection_ui import WordSelectionUI
from src.ui.games.article_selection_ui import ArticleSelectionUI
from src.ui.games.fill_blank_ui import FillBlankUI
from src.ui.games.error_detection_ui import ErrorDetectionUI


# Game registry mapping game mode names to UI classes
GAME_UI_REGISTRY = {
    "German → English": TranslationUI,
    "English → German": TranslationUI,
    "Word Selection (EN → DE)": WordSelectionUI,
    "Article Selection (der/die/das)": ArticleSelectionUI,
    "Fill-in-the-Blank": FillBlankUI,
    "Error Detection": ErrorDetectionUI,
}


def get_game_ui(game_mode: str):
    """
    Get the appropriate game UI for the given game mode.

    Args:
        game_mode: Name of the game mode

    Returns:
        Instance of the appropriate game UI class

    Raises:
        ValueError: If game mode is not recognized
    """
    ui_class = GAME_UI_REGISTRY.get(game_mode)
    if ui_class is None:
        raise ValueError(f"Unknown game mode: {game_mode}")
    return ui_class()
