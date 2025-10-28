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
    meaning: str = Field(description="English meaning of the noun")
    example_sentence: str = Field(description="Example German sentence using the noun with the correct article in this case")
    example_translation: str = Field(description="English translation of the example sentence")
    distractor_articles: list[str] = Field(description="Incorrect article options (2-3 alternatives)")
    explanation: str = Field(description="Brief explanation of the grammatical rule")


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


class VerbConjugationExercise(BaseModel):
    """Model for verb conjugation game."""
    infinitive: str = Field(description="German verb in infinitive form")
    english_meaning: str = Field(description="English translation of the verb")
    pronoun: str = Field(description="German pronoun (ich/du/er/sie/es/wir/ihr/sie/Sie)")
    tense: str = Field(description="Tense to conjugate (Präsens/Präteritum/Perfekt/etc)")
    correct_conjugation: str = Field(description="Correct conjugated form")
    example_sentence: str = Field(description="Example sentence using the conjugated verb")
    example_translation: str = Field(description="English translation of example sentence")
    explanation: str = Field(description="Brief explanation of conjugation pattern")


class SpeedTranslationExercise(BaseModel):
    """Model for speed translation game."""
    german_phrase: str = Field(description="German word or short phrase to translate")
    english_translation: str = Field(description="Correct English translation")
    difficulty: int = Field(description="Difficulty level 1-5 (1=easiest, affects time limit)")
    category: str = Field(description="Category: food/travel/common/verbs/etc")


class ConversationTurn(BaseModel):
    """Model for a single turn in conversation."""
    speaker: str = Field(description="Who is speaking: 'ai' or 'user'")
    german_text: str = Field(description="German dialogue text")
    english_translation: str = Field(description="English translation")
    options: list[str] = Field(default=[], description="Response options for user (empty for AI turns)")
    correct_option_index: int = Field(default=-1, description="Index of correct option (0-based, -1 for AI turns)")
    explanation: str = Field(default="", description="Why this option is correct")


class ConversationExercise(BaseModel):
    """Model for conversation builder game."""
    scenario: str = Field(description="Conversation scenario (restaurant/shopping/travel/etc)")
    scenario_description: str = Field(description="Brief description of the situation in English")
    turns: list[ConversationTurn] = Field(description="List of conversation turns (AI and user alternating)")
    learning_focus: str = Field(description="What this conversation teaches (formal/informal/vocab/etc)")
