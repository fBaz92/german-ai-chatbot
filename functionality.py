"""
Base functionality interface for chatbot functionalities.
"""
from abc import ABC, abstractmethod
from typing import Any, Dict


class Functionality(ABC):
    """
    Abstract base class for chatbot functionalities.
    Each functionality represents a specific capability of the chatbot.
    """
    
    @abstractmethod
    def get_name(self) -> str:
        """Return the name of this functionality."""
        pass
    
    @abstractmethod
    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute this functionality with the given context.
        
        Args:
            context: Dictionary containing execution context
            
        Returns:
            Dictionary containing execution results
        """
        pass
