"""
Pydantic models for game responses and validations.
"""
from pydantic import BaseModel, Field


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


class WordSelectionExercise(BaseModel):
    """Model for word selection game where users build German translation by selecting words."""
    english_sentence: str = Field(description="The English sentence to translate")
    correct_words: list[str] = Field(description="The correct German words in order (including punctuation)")
    distractor_words: list[str] = Field(description="Additional credible but incorrect German words (20-30% more than correct words)")
    explanation: str = Field(description="Brief explanation of the grammar and vocabulary used")


class AnswerValidation(BaseModel):
    """Model for answer validation."""
    is_correct: bool = Field(description="Whether the answer is correct")
    feedback: str = Field(description="Feedback message for the user")
    correct_answer: str = Field(description="The correct answer if user was wrong")
    explanation: str = Field(description="Explanation of why the answer is correct/incorrect")
