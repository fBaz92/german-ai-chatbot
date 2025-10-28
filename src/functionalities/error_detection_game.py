"""
Error Detection Game Functionality.
Interactive game where users find and correct errors in German sentences.
"""
from typing import Dict, Any, Optional
from src.functionalities.base import Functionality
from src.data.verb_loader import VerbLoader
from src.ai.datapizza_api import DatapizzaAPI
from src.models.game_models import ErrorDetectionExercise


class ErrorDetectionGameFunctionality(Functionality):
    """
    Interactive error detection game functionality.
    Users identify and correct intentional errors in German sentences.
    """

    def __init__(self, api: Optional[DatapizzaAPI] = None, csv_path: str = None):
        """
        Initialize the Error Detection Game.

        Args:
            api: DatapizzaAPI instance for exercise generation
            csv_path: Path to verbs CSV file (optional)
        """
        self.api = api
        self.verb_loader = VerbLoader(csv_path)
        self.incorrect_sentence = None
        self.correct_sentence = None
        self.error_type = None
        self.error_location = None
        self.explanation = None
        self.english_translation = None
        self.difficulty_range = (1, 5)
        self.tense = "Präsens"
        self.score = 0
        self.attempts = 0
        self.game_active = False
        self.hint_level = 0

    def get_name(self) -> str:
        """Return the name of this functionality."""
        return "error_detection_game"

    def start_game(self, difficulty: tuple = (1, 5), tense: str = "Präsens") -> Dict[str, Any]:
        """
        Start a new error detection game.

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
            "message": f"✅ Error Detection Game started! Difficulty: {difficulty[0]}-{difficulty[1]}, Tense: {tense}"
        }

    def next_exercise(self) -> Dict[str, Any]:
        """
        Generate the next error detection exercise.

        Returns:
            Dictionary with the new exercise
        """
        if not self.api:
            return {
                "success": False,
                "error": "API not configured. Use DatapizzaAPI."
            }

        # Get random verb
        verb = self.verb_loader.get_random_verb(
            min_freq=self.difficulty_range[0],
            max_freq=self.difficulty_range[1]
        )

        if not verb:
            return {
                "success": False,
                "error": "No verbs found for the selected difficulty."
            }

        # Generate error detection exercise using AI
        prompt = f"""
Generate an error detection exercise for German language learners.

Use the verb "{verb['Verbo']}" ({verb['English']}) in {self.tense}.
Difficulty level: {verb.get('Frequenza', 3)}/5 (1=easiest, 5=hardest)

Create an exercise with:
1. An INCORRECT German sentence (with ONE intentional error)
2. The CORRECT version of that sentence
3. The type of error (article/verb/word_order/case/spelling)
4. The specific incorrect word or phrase
5. Clear explanation of the error and correction
6. English translation of the correct sentence

Types of errors by difficulty:
- Difficulty 1-2: Wrong article (der/die/das) or simple verb conjugation
- Difficulty 3-4: Wrong case, verb tense, or adjective ending
- Difficulty 5: Word order in subordinate clauses, subjunctive mood, or subtle grammar

Example:
- incorrect_sentence: "Ich gehe zum Schule."
- correct_sentence: "Ich gehe zur Schule."
- error_type: "article"
- error_location: "zum"
- explanation: "Schule is feminine, so it requires 'zur' (zu der) not 'zum' (zu dem)"
- english_translation: "I go to school."

Make the error realistic (something learners commonly make).

RESPOND IN ENGLISH. All explanations must be in English.
"""

        try:
            response = self.api.client.structured_response(
                input=prompt,
                output_cls=ErrorDetectionExercise
            )

            if response.structured_data and len(response.structured_data) > 0:
                exercise_data = response.structured_data[0]

                # Store data
                self.incorrect_sentence = exercise_data.incorrect_sentence
                self.correct_sentence = exercise_data.correct_sentence
                self.error_type = exercise_data.error_type
                self.error_location = exercise_data.error_location
                self.explanation = exercise_data.explanation
                self.english_translation = exercise_data.english_translation

                self.hint_level = 0

                return {
                    "success": True,
                    "sentence": self.incorrect_sentence,
                    "message": f"Find the error: {self.incorrect_sentence}"
                }
            else:
                return {
                    "success": False,
                    "error": "Error generating exercise."
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }

    def check_answer(self, user_answer: str) -> Dict[str, Any]:
        """
        Check if the user's correction is correct.

        Args:
            user_answer: User's corrected sentence

        Returns:
            Dictionary with validation results
        """
        if not self.incorrect_sentence:
            return {
                "success": False,
                "error": "No active exercise."
            }

        self.attempts += 1

        # Normalize for comparison (strip whitespace, lowercase for flexible matching)
        user_normalized = user_answer.strip().lower()
        correct_normalized = self.correct_sentence.strip().lower()

        # Check if answer matches correct sentence (allow minor variations)
        is_correct = user_normalized == correct_normalized

        if is_correct:
            self.score += 1
            percentage = int(self.score / self.attempts * 100)

            return {
                "success": True,
                "is_correct": True,
                "message": f"✅ Correct! You found and fixed the error.\n\n**Error type:** {self.error_type}\n\n**Incorrect:** {self.error_location}\n\n💬 {self.explanation}\n\n**English:** {self.english_translation}\n\n({self.score}/{self.attempts} = {percentage}%)",
                "correct_answer": self.correct_sentence
            }
        else:
            percentage = int(self.score / self.attempts * 100) if self.attempts > 0 else 0

            return {
                "success": True,
                "is_correct": False,
                "message": f"❌ Not quite. Your answer: '{user_answer}'\n\n✅ **Correct sentence:** {self.correct_sentence}\n\n**Error type:** {self.error_type}\n\n**What was wrong:** {self.error_location}\n\n💬 {self.explanation}\n\n**English:** {self.english_translation}\n\n📊 Score: {self.score}/{self.attempts} ({percentage}%)",
                "correct_answer": self.correct_sentence
            }

    def get_hint(self) -> Dict[str, Any]:
        """
        Get progressive hint for the current exercise.

        Returns:
            Dictionary with hint
        """
        if not self.incorrect_sentence or not self.correct_sentence:
            return {
                "success": False,
                "error": "No active exercise."
            }

        self.hint_level += 1

        hints = []

        # Hint 1: Error type
        if self.hint_level >= 1:
            hints.append(f"🔹 **Error type:** {self.error_type}")

        # Hint 2: English translation
        if self.hint_level >= 2:
            hints.append(f"🔹 **English:** {self.english_translation}")

        # Hint 3: Which word/phrase is wrong
        if self.hint_level >= 3:
            hints.append(f"🔹 **Look at this word:** {self.error_location}")

        # Max hints reached - show full answer
        if self.hint_level >= 4:
            return {
                "success": True,
                "message": f"💡 **Correct sentence:** {self.correct_sentence}\n\n💬 {self.explanation}",
                "max_hints": True
            }

        hint_text = "\n".join(hints)
        return {
            "success": True,
            "message": f"💡 **Hint {self.hint_level}/3:**\n\n{hint_text}",
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
        return {
            "functionality": "error_detection_game",
            "status": "executed",
            "message": "Use the Streamlit interface to play the error detection game.",
            "data": {}
        }
