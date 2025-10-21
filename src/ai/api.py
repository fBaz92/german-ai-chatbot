"""
AI Chatbot API interface for handling questions and answers.
"""
from abc import ABC, abstractmethod
from typing import Dict, Any


class AIChatbotAPI(ABC):
    """
    Abstract base class for AI Chatbot API.
    This interface will be implemented with actual AI chatbot logic.
    """
    
    @abstractmethod
    def receive_question(self, question: str) -> Dict[str, Any]:
        """
        Receive and process a question.
        
        Args:
            question: The question text
            
        Returns:
            Dictionary containing question processing results
        """
        pass
    
    @abstractmethod
    def generate_answer(self, question: str, context: Dict[str, Any] = None) -> str:
        """
        Generate an answer for the given question.
        
        Args:
            question: The question text
            context: Optional context for answer generation
            
        Returns:
            The generated answer
        """
        pass
    
    @abstractmethod
    def check_answer(self, question: str, user_answer: str, correct_answer: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Check if the user's answer is correct.
        
        Args:
            question: The original question
            user_answer: The user's answer
            correct_answer: The correct answer (optional, for comparison)
            context: Additional context for validation (optional)
            
        Returns:
            Dictionary with keys:
                - is_correct: bool
                - correct_answer: str (if is_correct is False)
                - feedback: str (optional feedback message)
        """
        pass
    
    @abstractmethod
    def respond_with_error(self, error_message: str, correct_answer: str) -> str:
        """
        Format and return an error response with the correct answer.
        
        Args:
            error_message: Description of the error
            correct_answer: The correct answer
            
        Returns:
            Formatted error response
        """
        pass

