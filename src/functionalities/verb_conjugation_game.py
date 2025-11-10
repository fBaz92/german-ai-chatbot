"""
Verb Conjugation Game Functionality.
Interactive game where users conjugate German verbs correctly.
"""
import random
from typing import Dict, Any, Optional
from src.functionalities.base import Functionality
from src.data.verb_loader import VerbLoader
from src.ai.datapizza_api import DatapizzaAPI
from src.models.game_models import VerbConjugationExercise


class VerbConjugationGameFunctionality(Functionality):
    """
    Interactive verb conjugation game functionality.
    Users type the correct conjugated form of German verbs.
    """

    PRONOUNS = ["ich", "du", "er/sie/es", "wir", "ihr", "sie/Sie"]

    def __init__(self, api: Optional[DatapizzaAPI] = None, csv_path: str = None):
        """
        Initialize the Verb Conjugation Game.

        Args:
            api: DatapizzaAPI instance for exercise generation
            csv_path: Path to verbs CSV file (optional)
        """
        self.api = api
        self.verb_loader = VerbLoader(csv_path)
        self.current_infinitive = None
        self.current_pronoun = None
        self.current_tense = None
        self.correct_conjugation = None
        self.english_meaning = None
        self.example_sentence = None
        self.example_translation = None
        self.explanation = None
        self.difficulty_range = (1, 5)
        self.score = 0
        self.attempts = 0
        self.game_active = False
        self.hint_level = 0
        self.selected_tense = "Präsens"
        self.focus_item = None

    def get_name(self) -> str:
        """Return the name of this functionality."""
        return "verb_conjugation_game"

    def start_game(self, difficulty: tuple = (1, 5), tense: str = "Präsens") -> Dict[str, Any]:
        """
        Start a new verb conjugation game.

        Args:
            difficulty: Tuple of (min_difficulty, max_difficulty)
            tense: Verb tense to practice

        Returns:
            Dictionary with game start information
        """
        self.difficulty_range = difficulty
        self.selected_tense = tense
        self.score = 0
        self.attempts = 0
        self.game_active = True

        return {
            "success": True,
            "message": f"✅ Verb Conjugation Game started! Difficulty: {difficulty[0]}-{difficulty[1]}, Tense: {tense}"
        }

    def next_exercise(self) -> Dict[str, Any]:
        """
        Generate the next verb conjugation exercise.

        Returns:
            Dictionary with the new exercise
        """
        if not self.api:
            return {
                "success": False,
                "error": "API not configured. Use DatapizzaAPI."
            }

        focus_verb = None
        if self.focus_item and self.focus_item.get("item_type") == "verb":
            focus_verb = self.verb_loader.get_verb_by_name(self.focus_item.get("item_key", ""))

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

        # Select random pronoun
        pronoun = random.choice(self.PRONOUNS)

        # Generate verb conjugation exercise using AI
        prompt = f"""
Generate a German verb conjugation exercise for language learners using this specific verb:

Verb (Infinitive): {verb['Infinitiv']}
English meaning: {verb['English']}
Difficulty level: {verb.get('Frequenz', 3)}/5

IMPORTANT: You MUST use the verb "{verb['Infinitiv']}" provided above.

Create an exercise with:
1. The infinitive form: {verb['Infinitiv']}
2. English meaning of the verb
3. Pronoun to conjugate with: {pronoun}
4. Tense: {self.selected_tense}
5. The correct conjugated form for this pronoun + tense combination
6. An example German sentence using the conjugated verb with this pronoun
7. English translation of the example sentence
8. Brief explanation of the conjugation pattern (1 sentence)

Conjugation guidelines:
- For Perfekt tense: provide the full construction (e.g., "ich habe gemacht", "er ist gegangen")
- For Präteritum: provide the simple past form (e.g., "ich ging", "du machtest")
- For Präsens: provide present tense (e.g., "ich gehe", "du machst")
- For Konjunktiv II: provide conditional form (e.g., "ich würde gehen", "ich ginge")
- Be accurate with irregular verbs and stem changes

RESPOND IN ENGLISH for explanations, but German for the verb forms.
"""

        try:
            response = self.api.client.structured_response(
                input=prompt,
                output_cls=VerbConjugationExercise
            )

            if response.structured_data and len(response.structured_data) > 0:
                exercise_data = response.structured_data[0]

                # Store data
                self.current_infinitive = exercise_data.infinitive
                self.english_meaning = exercise_data.english_meaning
                self.current_pronoun = exercise_data.pronoun
                self.current_tense = exercise_data.tense
                self.correct_conjugation = exercise_data.correct_conjugation
                self.example_sentence = exercise_data.example_sentence
                self.example_translation = exercise_data.example_translation
                self.explanation = exercise_data.explanation

                self.hint_level = 0
                self.focus_item = None

                return {
                    "success": True,
                    "sentence": f"{self.current_infinitive} + {self.current_pronoun} + {self.current_tense}",
                    "infinitive": self.current_infinitive,
                    "pronoun": self.current_pronoun,
                    "tense": self.current_tense,
                    "english_meaning": self.english_meaning,
                    "message": f"Conjugate: {self.current_infinitive} ({self.english_meaning}) with {self.current_pronoun} in {self.current_tense}"
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

    def check_translation(self, user_answer: str) -> Dict[str, Any]:
        """
        Check if the user's conjugation is correct.

        Args:
            user_answer: User's conjugated verb form

        Returns:
            Dictionary with validation results
        """
        if not self.current_infinitive:
            return {
                "success": False,
                "error": "No active exercise."
            }

        self.attempts += 1

        # Normalize for comparison (lowercase, strip whitespace)
        user_normalized = user_answer.strip().lower()
        correct_normalized = self.correct_conjugation.strip().lower()

        is_correct = user_normalized == correct_normalized

        if is_correct:
            self.score += 1
            percentage = int(self.score / self.attempts * 100)
            return {
                "success": True,
                "is_correct": True,
                "message": f"✅ Correct! **{self.correct_conjugation}**\n\n📖 **Verb:** {self.current_infinitive} ({self.english_meaning})\n\n💬 **{self.explanation}**\n\n📝 **Example:**\n🇩🇪 {self.example_sentence}\n🇬🇧 {self.example_translation}\n\n📊 Score: {self.score}/{self.attempts} ({percentage}%)",
                "correct_answer": self.correct_conjugation
            }
        else:
            percentage = int(self.score / self.attempts * 100) if self.attempts > 0 else 0

            return {
                "success": True,
                "is_correct": False,
                "message": f"❌ Wrong. You wrote '{user_answer}'.\n\n✅ **Correct answer:** {self.correct_conjugation}\n\n📖 **Verb:** {self.current_infinitive} ({self.english_meaning})\n\n💬 **{self.explanation}**\n\n📝 **Example:**\n🇩🇪 {self.example_sentence}\n🇬🇧 {self.example_translation}\n\n📊 Score: {self.score}/{self.attempts} ({percentage}%)",
                "correct_answer": self.correct_conjugation
            }

    def get_hint(self) -> Dict[str, Any]:
        """
        Get progressive hint for the current exercise.

        Returns:
            Dictionary with hint
        """
        if not self.current_infinitive or not self.correct_conjugation:
            return {
                "success": False,
                "error": "No active exercise."
            }

        self.hint_level += 1

        hints = []

        # Hint 1: Explanation
        if self.hint_level >= 1:
            hints.append(f"🔹 **{self.explanation}**")

        # Hint 2: Number of words (for compound tenses)
        if self.hint_level >= 2:
            word_count = len(self.correct_conjugation.split())
            if word_count > 1:
                hints.append(f"🔹 **Words:** {word_count} words (e.g., auxiliary + past participle)")
            else:
                hints.append(f"🔹 **Single word conjugation**")

        # Hint 3: First letter(s)
        if self.hint_level >= 3:
            words = self.correct_conjugation.split()
            if len(words) > 1:
                hints.append(f"🔹 **Starts with:** {words[0][:2]}...")
            else:
                hints.append(f"🔹 **First letters:** {self.correct_conjugation[:2]}...")

        # Max hints reached - show full answer
        if self.hint_level >= 4:
            return {
                "success": True,
                "message": f"💡 **Full answer:** {self.correct_conjugation}\n\n📝 **Example:**\n🇩🇪 {self.example_sentence}\n🇬🇧 {self.example_translation}",
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
Tense: {self.selected_tense}
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
            "functionality": "verb_conjugation_game",
            "status": "executed",
            "message": "Use the Streamlit interface to play the verb conjugation game.",
            "data": {}
        }
