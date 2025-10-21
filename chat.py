"""
Chat class for managing chatbot interactions.
"""
from typing import List, Dict, Any, Optional
from functionality import Functionality
from ai_chatbot_api import AIChatbotAPI


class Chat:
    """
    Main chat class that manages functionalities and handles interactions.
    """
    
    def __init__(self, api: AIChatbotAPI):
        """
        Initialize the Chat with an AI Chatbot API.
        
        Args:
            api: An instance of AIChatbotAPI for handling AI logic
        """
        self.api = api
        self.functionalities: Dict[str, Functionality] = {}
        self.active_functionality: Optional[Functionality] = None
        self.conversation_history: List[Dict[str, Any]] = []
    
    def add_functionality(self, functionality: Functionality) -> None:
        """
        Add a functionality to the chat.
        
        Args:
            functionality: A Functionality instance to add
        """
        name = functionality.get_name()
        self.functionalities[name] = functionality
        print(f"Added functionality: {name}")
    
    def remove_functionality(self, name: str) -> bool:
        """
        Remove a functionality from the chat.
        
        Args:
            name: Name of the functionality to remove
            
        Returns:
            True if removed, False if not found
        """
        if name in self.functionalities:
            del self.functionalities[name]
            if self.active_functionality and self.active_functionality.get_name() == name:
                self.active_functionality = None
            return True
        return False
    
    def list_functionalities(self) -> List[str]:
        """
        Get a list of available functionality names.
        
        Returns:
            List of functionality names
        """
        return list(self.functionalities.keys())
    
    def select_functionality(self, name: str) -> bool:
        """
        Select a functionality to use.
        
        Args:
            name: Name of the functionality to select
            
        Returns:
            True if selected, False if not found
        """
        if name in self.functionalities:
            self.active_functionality = self.functionalities[name]
            print(f"Selected functionality: {name}")
            return True
        print(f"Functionality '{name}' not found")
        return False
    
    def handle_interaction(self, user_input: str) -> Dict[str, Any]:
        """
        Handle a user interaction.
        
        Args:
            user_input: The user's input text
            
        Returns:
            Dictionary containing interaction results
        """
        # Receive and process the question
        question_result = self.api.receive_question(user_input)
        
        # Generate an answer
        context = {"functionality": self.active_functionality.get_name() if self.active_functionality else None}
        answer = self.api.generate_answer(user_input, context)
        
        # Execute active functionality if any
        functionality_result = None
        if self.active_functionality:
            functionality_result = self.active_functionality.execute({
                "question": user_input,
                "answer": answer,
                "context": context
            })
        
        # Store in conversation history
        interaction = {
            "user_input": user_input,
            "answer": answer,
            "functionality_result": functionality_result,
            "timestamp": self._get_timestamp()
        }
        self.conversation_history.append(interaction)
        
        return interaction
    
    def check_user_response(self, question: str, user_answer: str) -> Dict[str, Any]:
        """
        Check if the user's answer is correct.
        
        Args:
            question: The original question
            user_answer: The user's answer
            
        Returns:
            Dictionary with validation results
        """
        check_result = self.api.check_answer(question, user_answer)
        
        if not check_result.get("is_correct", False):
            error_response = self.api.respond_with_error(
                check_result.get("feedback", "Incorrect answer"),
                check_result.get("correct_answer", "")
            )
            check_result["error_response"] = error_response
        
        return check_result
    
    def get_conversation_history(self) -> List[Dict[str, Any]]:
        """
        Get the conversation history.
        
        Returns:
            List of interaction dictionaries
        """
        return self.conversation_history
    
    def clear_history(self) -> None:
        """Clear the conversation history."""
        self.conversation_history = []
    
    def _get_timestamp(self) -> str:
        """Get current timestamp as string."""
        from datetime import datetime
        return datetime.now().isoformat()
