"""
German AI Chatbot - A modular command-line chatbot boilerplate.
"""

__version__ = "1.0.0"

from .chat import Chat
from .ai_chatbot_api import AIChatbotAPI
from .functionality import Functionality
from .mock_ai_api import MockAIChatbotAPI

__all__ = [
    "Chat",
    "AIChatbotAPI",
    "Functionality",
    "MockAIChatbotAPI",
]
