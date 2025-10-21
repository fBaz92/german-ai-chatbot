"""
Mock implementation of AI Chatbot API for testing and demonstration.
This should be replaced with actual AI chatbot logic.
"""
from typing import Dict, Any
from ai_chatbot_api import AIChatbotAPI


class MockAIChatbotAPI(AIChatbotAPI):
    """
    Mock implementation of AIChatbotAPI.
    Replace this with your actual AI chatbot implementation.
    """
    
    def receive_question(self, question: str) -> Dict[str, Any]:
        """
        Receive and process a question.
        
        Args:
            question: The question text
            
        Returns:
            Dictionary containing question processing results
        """
        return {
            "question": question,
            "processed": True,
            "word_count": len(question.split())
        }
    
    def generate_answer(self, question: str, context: Dict[str, Any] = None) -> str:
        """
        Generate a mock answer for the given question.
        
        Args:
            question: The question text
            context: Optional context for answer generation
            
        Returns:
            The generated answer
        """
        # This is a mock implementation - replace with actual AI logic
        return f"Mock answer for: '{question}'"
    
    def check_answer(self, question: str, user_answer: str) -> Dict[str, Any]:
        """
        Check if the user's answer is correct (mock implementation).
        
        Args:
            question: The original question
            user_answer: The user's answer
            
        Returns:
            Dictionary with validation results
        """
        # Mock validation logic - replace with actual implementation
        # For demonstration, we'll consider answers with more than 3 words as correct
        is_correct = len(user_answer.split()) > 3
        
        result = {
            "is_correct": is_correct,
            "feedback": "Good answer!" if is_correct else "Please provide a more detailed answer"
        }
        
        if not is_correct:
            result["correct_answer"] = "A detailed answer with proper explanation"
        
        return result
    
    def respond_with_error(self, error_message: str, correct_answer: str) -> str:
        """
        Format and return an error response with the correct answer.
        
        Args:
            error_message: Description of the error
            correct_answer: The correct answer
            
        Returns:
            Formatted error response
        """
        return f"❌ {error_message}\n✓ Correct answer: {correct_answer}"
