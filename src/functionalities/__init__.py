"""
Functionalities module for chatbot capabilities.
"""
from src.functionalities.base import Functionality
from src.functionalities.translation_game import TranslationGameFunctionality
from src.functionalities.inverse_translation_game import InverseTranslationGameFunctionality

__all__ = [
    'Functionality',
    'TranslationGameFunctionality',
    'InverseTranslationGameFunctionality'
]

