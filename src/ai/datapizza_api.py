"""
AI Chatbot API implementation using Datapizza with Ollama or Google Gemini.
"""
import os
from pathlib import Path
from typing import Dict, Any, Literal
from dotenv import load_dotenv
from datapizza.clients.openai_like import OpenAILikeClient
from datapizza.clients.google import GoogleClient
from pydantic import BaseModel, Field
from src.ai.api import AIChatbotAPI

# Load environment variables from .env file
env_path = Path(__file__).parent.parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


# Pydantic models for structured responses
class GermanSentence(BaseModel):
    """Model for a German sentence generation."""
    sentence: str = Field(description="The German sentence")
    translation: str = Field(description="English translation of the sentence")
    explanation: str = Field(description="Brief explanation of grammar used")

class EnglishSentence(BaseModel):
    """Model for an English sentence generation."""
    sentence: str = Field(description="The English sentence")
    translation: str = Field(description="German translation of the sentence")
    explanation: str = Field(description="Brief explanation of grammar used")


class AnswerValidation(BaseModel):
    """Model for answer validation."""
    is_correct: bool = Field(description="Whether the answer is correct")
    feedback: str = Field(description="Feedback message for the user")
    correct_answer: str = Field(description="The correct answer if user was wrong")
    explanation: str = Field(description="Explanation of why the answer is correct/incorrect")


class SimpleResponse(BaseModel):
    """Model for simple text responses."""
    answer: str = Field(description="The response text")


class DatapizzaAPI(AIChatbotAPI):
    """
    Implementation of AIChatbotAPI using Datapizza library.
    Supports both Ollama (local) and Google Gemini (cloud).
    """
    
    def __init__(
        self, 
        provider: Literal["ollama", "google"] = "ollama",
        api_key: str = None,
        base_url: str = "http://localhost:11434/v1",
        model: str = None
    ):
        """
        Initialize the Datapizza API client.
        
        Args:
            provider: "ollama" for local or "google" for Google Gemini
            api_key: API key (for Google, reads from GEMINI_KEY env if None)
            base_url: Base URL for Ollama API
            model: Model to use (defaults: gemma3:1b for Ollama, gemini-2.0-flash-exp for Google)
        """
        self.provider = provider
        
        system_prompt = "You are a German language tutor. Generate simple, clear sentences. Always respond in ENGLISH. All feedback, explanations, and messages must be in English, not German. Respond with valid JSON only. No extra text, no emojis."
        
        if provider == "google":
            # Google Gemini client
            if api_key is None:
                api_key = os.getenv("GEMINI_KEY")
            
            if not api_key:
                raise ValueError("GEMINI_KEY not found in environment. Set it with: export GEMINI_KEY='your-key'")
            
            self.model = model or "gemini-2.5-flash"
            self.client = GoogleClient(
                api_key=api_key,
                model=self.model,
                system_prompt=system_prompt,
            )
            
        else:  # ollama
            # Ollama local client
            self.model = model or "gemma3:1b"
            self.client = OpenAILikeClient(
                api_key="",  # Ollama doesn't require an API key
                model=self.model,
                system_prompt=system_prompt,
                base_url=base_url
            )
    
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
        Generate an answer for the given question using Ollama.
        
        Args:
            question: The question text
            context: Optional context for answer generation
            
        Returns:
            The generated answer
        """
        try:
            response = self.client.structured_response(
                input=question,
                output_cls=SimpleResponse
            )
            
            if response.structured_data and len(response.structured_data) > 0:
                return response.structured_data[0].answer
            else:
                return "Sorry, I couldn't generate a response."
                
        except Exception as e:
            print(f"Error generating answer: {e}")
            return f"Error generating response: {str(e)}"
    
    def check_answer(self, question: str, user_answer: str, correct_answer: str = None, context: Dict[str, Any] = None) -> Dict[str, Any]:
        """
        Check if the user's answer is correct using AI validation.
        
        Args:
            question: The original question
            user_answer: The user's answer
            correct_answer: The correct answer for comparison (if provided)
            context: Additional context for validation
            
        Returns:
            Dictionary with validation results
        """
        try:
            # Build validation prompt based on what we have
            if correct_answer:
                # We have the correct answer - do strict comparison
                validation_prompt = f"""
Question: {question}

User's answer: {user_answer}
Correct answer: {correct_answer}

Compare the user's answer with the correct answer.

IMPORTANT: 
- Be strict in your evaluation
- If the verbs are different, mark as INCORRECT
- If the core meaning changed, mark as INCORRECT
- Grammar and tense must be correct
- Minor variations in word choice are OK if meaning is preserved

RESPOND IN ENGLISH ONLY. All feedback, explanations, and messages must be in English.

Return a JSON object with:
- is_correct: true/false
- feedback: Brief message for the user (IN ENGLISH)
- correct_answer: The correct answer (IN GERMAN)
- explanation: Why it's correct/incorrect (IN ENGLISH)
"""
            else:
                # No correct answer provided - general validation
                validation_prompt = f"""
{question}

User's answer: {user_answer}

Evaluate if the answer is correct. Consider:
- Grammar correctness
- Proper verb usage
- Sentence structure
- Meaning preservation

RESPOND IN ENGLISH ONLY. All feedback and explanations must be in English.

If uncertain, be lenient but provide constructive feedback (in English).
"""
            
            response = self.client.structured_response(
                input=validation_prompt,
                output_cls=AnswerValidation
            )
            
            if response.structured_data and len(response.structured_data) > 0:
                validation = response.structured_data[0]
                return {
                    "is_correct": validation.is_correct,
                    "feedback": validation.feedback,
                    "correct_answer": validation.correct_answer,
                    "explanation": validation.explanation
                }
            else:
                return {
                    "is_correct": False,
                    "feedback": "Could not validate the answer.",
                    "correct_answer": "",
                    "explanation": ""
                }
                
        except Exception as e:
            print(f"Error checking answer: {e}")
            return {
                "is_correct": False,
                "feedback": f"Validation error: {str(e)}",
                "correct_answer": "",
                "explanation": ""
            }
    
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
