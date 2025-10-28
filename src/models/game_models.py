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


class ArticleExercise(BaseModel):
    """Model for article selection game (der/die/das)."""
    noun: str = Field(description="The German noun (without article)")
    correct_article: str = Field(description="The correct article (der/die/das/den/dem/des)")
    case: str = Field(description="The grammatical case (Nominativ/Akkusativ/Dativ/Genitiv)")
    context_sentence: str = Field(description="Example sentence using the noun with context")
    distractor_articles: list[str] = Field(description="Incorrect article options (2-3 alternatives)")
    explanation: str = Field(description="Explanation of why this article is correct")


class FillInBlankExercise(BaseModel):
    """Model for fill-in-the-blank game."""
    sentence_with_blank: str = Field(description="German sentence with [BLANK] placeholder")
    correct_answer: str = Field(description="The correct word to fill in the blank")
    hint: str = Field(description="Hint about the missing word (word type, context)")
    english_translation: str = Field(description="English translation of the complete sentence")
    explanation: str = Field(description="Explanation of grammar/vocabulary")


class ErrorDetectionExercise(BaseModel):
    """Model for error detection game."""
    incorrect_sentence: str = Field(description="German sentence with one intentional error")
    correct_sentence: str = Field(description="The correct version of the sentence")
    error_type: str = Field(description="Type of error (article/verb/word_order/case/spelling)")
    error_location: str = Field(description="The incorrect word or phrase")
    explanation: str = Field(description="Explanation of the error and correction")
    english_translation: str = Field(description="English translation of correct sentence")
