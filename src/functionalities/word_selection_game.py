"""
Word Selection Game Functionality.
Interactive game where users build German translations by selecting words in order.
"""
import random
from typing import Dict, Any, Optional, List
from src.functionalities.base import Functionality
from src.data.verb_loader import VerbLoader
from src.ai.datapizza_api import DatapizzaAPI
from src.models.game_models import WordSelectionExercise


class WordSelectionGameFunctionality(Functionality):
    """
    Interactive word selection game functionality.
    Users build German translations by selecting words in the correct order.
    """

    def __init__(self, api: Optional[DatapizzaAPI] = None, csv_path: str = None):
        """
        Initialize the Word Selection Game.

        Args:
            api: DatapizzaAPI instance for sentence generation
            csv_path: Path to verbs CSV file (optional)
        """
        self.api = api
        self.verb_loader = VerbLoader(csv_path)
        self.current_english_sentence = None
        self.correct_words = []
        self.all_words = []  # correct + distractors, shuffled
        self.difficulty_range = (1, 5)
        self.score = 0
        self.attempts = 0
        self.tense = "Präsens"
        self.game_active = False
        self.hint_level = 0
        self.explanation = ""
        self.focus_item = None
        self.current_verb = None

    def get_name(self) -> str:
        """Return the name of this functionality."""
        return "word_selection_game"

    def start_game(self, difficulty: tuple = (1, 5), tense: str = "Präsens") -> Dict[str, Any]:
        """
        Start a new word selection game.

        Args:
            difficulty: Tuple of (min_difficulty, max_difficulty)
            tense: Verb tense to practice

        Returns:
            Dictionary with game start information
        """
        self.difficulty_range = difficulty
        self.tense = tense
        self.score = 0
        self.attempts = 0
        self.game_active = True

        return {
            "success": True,
            "message": f"✅ Word Selection Game started! Difficulty: {difficulty[0]}-{difficulty[1]}, Tense: {tense}"
        }

    def next_sentence(self) -> Dict[str, Any]:
        """
        Generate the next sentence for word selection.

        Returns:
            Dictionary with the new sentence and words
        """
        if not self.api:
            return {
                "success": False,
                "error": "API not configured. Use DatapizzaAPI."
            }

        focus_verb = None
        if self.focus_item and self.focus_item.get("item_type") == "verb":
            focus_verb = self.verb_loader.get_verb_by_name(self.focus_item.get("item_key", ""))
            focus_tense = (self.focus_item.get("context") or {}).get("tense")
            if focus_tense:
                self.tense = focus_tense

        # Get random verb
        verb = focus_verb or self.verb_loader.get_random_verb(
            min_freq=self.difficulty_range[0],
            max_freq=self.difficulty_range[1]
        )

        if not verb:
            return {
                "success": False,
                "error": "No verbs found for the selected difficulty."
            }

        # Generate sentence with words using AI
        prompt = f"""
            Generate an English sentence using the verb "{verb['English']}" ({verb['Verbo']}) in {self.tense}.
            Difficulty level: {verb.get('Frequenza', 3)}/5 (1=easiest, 5=hardest)

            Create a natural, everyday sentence that demonstrates proper use of this verb.

            IMPORTANT INSTRUCTIONS:
            1. Provide the correct German translation as a LIST OF WORDS (split by spaces, keep punctuation attached to words)
            2. Generate 20-30% ADDITIONAL credible but INCORRECT German words as distractors
            - Distractors should be plausible alternatives (wrong verb forms, wrong articles, wrong nouns, etc.)
            - Make them challenging but not impossible to distinguish
            - Examples of good distractors: wrong gender articles (der/die/das), wrong verb conjugations, similar nouns
            3. Explain the grammar briefly in English

            Example format:
            - english_sentence: "I eat an apple"
            - correct_words: ["Ich", "esse", "einen", "Apfel"]
            - distractor_words: ["isst", "essen", "ein", "der", "Äpfel", "Birne"]
            - explanation: "Using 'esse' (1st person singular) with accusative article 'einen' for masculine noun"

            RESPOND IN ENGLISH. The explanation must be in English.
            """

        try:
            response = self.api.client.structured_response(
                input=prompt,
                output_cls=WordSelectionExercise
            )

            if response.structured_data and len(response.structured_data) > 0:
                exercise_data = response.structured_data[0]

                # Store data
                self.current_english_sentence = exercise_data.english_sentence
                self.correct_words = exercise_data.correct_words
                self.explanation = exercise_data.explanation
                self.current_verb = verb['Verbo']

                # Combine and shuffle all words
                self.all_words = exercise_data.correct_words + exercise_data.distractor_words
                random.shuffle(self.all_words)

                self.hint_level = 0
                self.focus_item = None

                return {
                    "success": True,
                    "english_sentence": self.current_english_sentence,
                    "all_words": self.all_words,
                    "explanation": self.explanation,
                    "message": f"🇬🇧 {self.current_english_sentence}"
                }
            else:
                return {
                    "success": False,
                    "error": "Error generating sentence."
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }

    def check_word_selection(self, selected_words: List[str]) -> Dict[str, Any]:
        """
        Check if the user's word selection is correct.

        Args:
            selected_words: List of words selected by user in order

        Returns:
            Dictionary with validation results
        """
        if not self.current_english_sentence:
            return {
                "success": False,
                "error": "No active sentence."
            }

        self.attempts += 1

        # Normalize for comparison (handle punctuation and case)
        user_sentence = " ".join(selected_words).strip()
        correct_sentence = " ".join(self.correct_words).strip()

        # Check if sequences match
        is_correct = selected_words == self.correct_words

        if is_correct:
            self.score += 1
            percentage = int(self.score / self.attempts * 100)
            return {
                "success": True,
                "is_correct": True,
                "message": f"✅ Correct! Perfect word order. ({self.score}/{self.attempts} = {percentage}%)",
                "correct_answer": correct_sentence
            }
        else:
            percentage = int(self.score / self.attempts * 100) if self.attempts > 0 else 0

            # Provide detailed feedback
            feedback_parts = []

            # Check if they have the right words but wrong order
            if sorted(selected_words) == sorted(self.correct_words):
                feedback_parts.append("You have all the right words, but the order is wrong!")
            else:
                # Find wrong words
                wrong_words = [w for w in selected_words if w not in self.correct_words]
                if wrong_words:
                    feedback_parts.append(f"Wrong words used: {', '.join(wrong_words)}")

                # Find missing words
                missing_words = [w for w in self.correct_words if w not in selected_words]
                if missing_words:
                    feedback_parts.append(f"Missing words: {', '.join(missing_words)}")

            feedback = "\n".join(feedback_parts) if feedback_parts else "Try again!"

            return {
                "success": True,
                "is_correct": False,
                "message": f"❌ Wrong.\n\n{feedback}\n\n✅ **Correct answer:** {correct_sentence}\n\n💬 {self.explanation}\n\n📊 Score: {self.score}/{self.attempts} ({percentage}%)",
                "correct_answer": correct_sentence
            }

    def get_hint(self) -> Dict[str, Any]:
        """
        Get progressive hint for the current sentence.

        Returns:
            Dictionary with hint
        """
        if not self.current_english_sentence or not self.correct_words:
            return {
                "success": False,
                "error": "No active sentence."
            }

        self.hint_level += 1

        hints = []

        # Hint 1: Number of words
        if self.hint_level >= 1:
            hints.append(f"🔹 **Number of words:** {len(self.correct_words)}")

        # Hint 2: First word
        if self.hint_level >= 2:
            hints.append(f"🔹 **First word:** {self.correct_words[0]}")

        # Hint 3: Last word
        if self.hint_level >= 3:
            hints.append(f"🔹 **Last word:** {self.correct_words[-1]}")

        # Hint 4: Show first half of answer
        if self.hint_level >= 4:
            half_len = max(1, len(self.correct_words) // 2)
            half_words = self.correct_words[:half_len]
            hints.append(f"🔹 **First half:** {' '.join(half_words)}")

        # Max hints reached - show full answer
        if self.hint_level >= 5:
            return {
                "success": True,
                "message": f"💡 **Full answer:** {' '.join(self.correct_words)}",
                "max_hints": True
            }

        hint_text = "\n".join(hints)
        return {
            "success": True,
            "message": f"💡 **Hint {self.hint_level}/4:**\n\n{hint_text}",
            "max_hints": False
        }

    def get_score(self) -> Dict[str, Any]:
        """
        Get current score.

        Returns:
            Dictionary with score information
        """
        if self.attempts == 0:
            percentage = 0
        else:
            percentage = int(self.score / self.attempts * 100)

        return {
            "success": True,
            "message": f"""
                📊 Your Score:

                Correct: {self.score}/{self.attempts}
                Accuracy: {percentage}%
                Difficulty: {self.difficulty_range[0]}-{self.difficulty_range[1]}
                Tense: {self.tense}
                """.strip()
            }

    def stop_game(self) -> Dict[str, Any]:
        """
        Stop the current game.

        Returns:
            Dictionary with final score
        """
        self.game_active = False

        if self.attempts == 0:
            return {
                "success": True,
                "message": "Game stopped. You didn't answer any questions yet!"
            }

        percentage = int(self.score / self.attempts * 100)

        return {
            "success": True,
            "message": f"""
🎮 Game Over!

Final Score: {self.score}/{self.attempts} ({percentage}%)

{'🏆 Excellent!' if percentage >= 80 else '👍 Good job!' if percentage >= 60 else '💪 Keep practicing!'}
""".strip()
        }

    def execute(self, context: Dict[str, Any]) -> Dict[str, Any]:
        """
        Execute the functionality based on the context.

        Args:
            context: Dictionary with question, answer, and other context

        Returns:
            Dictionary with execution results
        """
        # This method is for CLI-style interaction
        # For Streamlit, we use the direct methods above
        return {
            "functionality": "word_selection_game",
            "status": "executed",
            "message": "Use the Streamlit interface to play the word selection game.",
            "data": {}
        }
