"""
Speed Translation Game Functionality.
Timed translation game where users translate words/phrases quickly.
"""
import time
from typing import Dict, Any, Optional
from src.functionalities.base import Functionality
from src.ai.datapizza_api import DatapizzaAPI
from src.models.game_models import SpeedTranslationExercise


class SpeedTranslationGameFunctionality(Functionality):
    """
    Speed translation game functionality.
    Users translate German phrases quickly for points.
    """

    # Time limits by difficulty (in seconds)
    TIME_LIMITS = {
        1: 15,  # Very easy
        2: 12,
        3: 10,
        4: 8,
        5: 6    # Very hard
    }

    def __init__(self, api: Optional[DatapizzaAPI] = None):
        """
        Initialize the Speed Translation Game.

        Args:
            api: DatapizzaAPI instance for exercise generation
        """
        self.api = api
        self.current_phrase = None
        self.correct_translation = None
        self.difficulty = 1
        self.category = None
        self.time_limit = 15
        self.start_time = None
        self.difficulty_range = (1, 5)
        self.score = 0
        self.attempts = 0
        self.game_active = False
        self.combo = 0  # Consecutive correct answers
        self.max_combo = 0
        self.total_time_bonus = 0

    def get_name(self) -> str:
        """Return the name of this functionality."""
        return "speed_translation_game"

    def start_game(self, difficulty: tuple = (1, 5), **kwargs) -> Dict[str, Any]:
        """
        Start a new speed translation game.

        Args:
            difficulty: Tuple of (min_difficulty, max_difficulty)

        Returns:
            Dictionary with game start information
        """
        self.difficulty_range = difficulty
        self.score = 0
        self.attempts = 0
        self.combo = 0
        self.max_combo = 0
        self.total_time_bonus = 0
        self.game_active = True

        return {
            "success": True,
            "message": f"✅ Speed Translation Game started! Difficulty: {difficulty[0]}-{difficulty[1]}\n\nTranslate quickly for bonus points!"
        }

    def next_exercise(self) -> Dict[str, Any]:
        """
        Generate the next speed translation exercise.

        Returns:
            Dictionary with the new exercise
        """
        if not self.api:
            return {
                "success": False,
                "error": "API not configured. Use DatapizzaAPI."
            }

        # Generate speed translation exercise using AI
        prompt = f"""
Generate a German speed translation exercise for language learners.

Difficulty range: {self.difficulty_range[0]}-{self.difficulty_range[1]} (1=easiest, 5=hardest)

Create an exercise with:
1. A German word or short phrase (1-4 words) appropriate for the difficulty level
2. The English translation
3. Exact difficulty level (1-5) based on:
   - Level 1: Common everyday words (Hallo, danke, ja)
   - Level 2: Basic nouns/verbs (Haus, gehen, Wasser)
   - Level 3: Common phrases (Wie geht's? Guten Morgen)
   - Level 4: Less common vocabulary or short sentences
   - Level 5: Idiomatic phrases or complex words
4. Category (food/travel/greetings/common/verbs/adjectives/phrases/idioms)

Guidelines:
- Keep it SHORT for speed translation (max 4 words)
- Choose difficulty within the specified range
- Variety in categories
- No complex grammar explanations needed

RESPOND IN ENGLISH.
"""

        try:
            response = self.api.client.structured_response(
                input=prompt,
                output_cls=SpeedTranslationExercise
            )

            if response.structured_data and len(response.structured_data) > 0:
                exercise_data = response.structured_data[0]

                # Store data
                self.current_phrase = exercise_data.german_phrase
                self.correct_translation = exercise_data.english_translation
                self.difficulty = exercise_data.difficulty
                self.category = exercise_data.category
                self.time_limit = self.TIME_LIMITS.get(self.difficulty, 10)
                self.start_time = time.time()

                return {
                    "success": True,
                    "sentence": self.current_phrase,
                    "difficulty": self.difficulty,
                    "category": self.category,
                    "time_limit": self.time_limit,
                    "message": f"Translate: {self.current_phrase}"
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
        Check if the user's translation is correct and calculate time bonus.

        Args:
            user_answer: User's translation

        Returns:
            Dictionary with validation results
        """
        if not self.current_phrase:
            return {
                "success": False,
                "error": "No active exercise."
            }

        self.attempts += 1

        # Calculate time taken
        time_taken = time.time() - self.start_time if self.start_time else 0
        time_remaining = max(0, self.time_limit - time_taken)
        is_timed_out = time_taken > self.time_limit

        # Normalize for comparison (lowercase, strip whitespace)
        user_normalized = user_answer.strip().lower()
        correct_normalized = self.correct_translation.strip().lower()

        is_correct = user_normalized == correct_normalized

        if is_correct:
            # Calculate points
            base_points = 10 * self.difficulty

            # Time bonus (up to 50% extra if answered quickly)
            time_bonus_multiplier = time_remaining / self.time_limit if not is_timed_out else 0
            time_bonus = int(base_points * 0.5 * time_bonus_multiplier)

            # Combo multiplier (5% per combo level, max 50%)
            combo_multiplier = min(self.combo * 0.05, 0.5)
            combo_bonus = int(base_points * combo_multiplier)

            total_points = base_points + time_bonus + combo_bonus

            self.score += total_points
            self.combo += 1
            self.max_combo = max(self.max_combo, self.combo)
            self.total_time_bonus += time_bonus

            percentage = int(self.score / (self.attempts * 10 * 3) * 100) if self.attempts > 0 else 0

            return {
                "success": True,
                "is_correct": True,
                "message": f"✅ Correct! **{self.correct_translation}**\n\n⚡ **Time:** {time_taken:.1f}s / {self.time_limit}s\n\n🎯 **Points:**\n• Base: +{base_points}\n• Time bonus: +{time_bonus}\n• Combo bonus (x{self.combo}): +{combo_bonus}\n• **Total: +{total_points} points**\n\n🔥 **Combo:** {self.combo}x\n\n📊 **Total Score:** {self.score} points ({self.attempts} answers)",
                "correct_answer": self.correct_translation,
                "points_earned": total_points,
                "time_taken": time_taken
            }
        else:
            # Reset combo on wrong answer
            self.combo = 0

            percentage = int(self.score / (self.attempts * 10 * 3) * 100) if self.attempts > 0 else 0

            timeout_msg = "\n\n⏰ **TIME'S UP!**" if is_timed_out else ""

            return {
                "success": True,
                "is_correct": False,
                "message": f"❌ Wrong. You wrote '{user_answer}'.{timeout_msg}\n\n✅ **Correct answer:** {self.correct_translation}\n\n⚡ **Time:** {time_taken:.1f}s / {self.time_limit}s\n\n💔 **Combo broken!**\n\n📊 **Total Score:** {self.score} points ({self.attempts} answers)",
                "correct_answer": self.correct_translation,
                "points_earned": 0,
                "time_taken": time_taken
            }

    def get_hint(self) -> Dict[str, Any]:
        """
        Get hint - shows first letter (costs combo).

        Returns:
            Dictionary with hint
        """
        if not self.current_phrase or not self.correct_translation:
            return {
                "success": False,
                "error": "No active exercise."
            }

        # Hint costs your combo
        self.combo = 0

        first_word = self.correct_translation.split()[0]
        hint = f"🔹 **First word starts with:** {first_word[:2]}..."

        return {
            "success": True,
            "message": f"💡 **Hint (Combo reset!):**\n\n{hint}",
            "max_hints": False
        }

    def get_score(self) -> Dict[str, Any]:
        """
        Get current score.

        Returns:
            Dictionary with score information
        """
        avg_points = int(self.score / self.attempts) if self.attempts > 0 else 0

        return {
            "success": True,
            "message": f"""
📊 Your Score:

Total Points: {self.score}
Answers: {self.attempts}
Average: {avg_points} pts/answer
Max Combo: {self.max_combo}x
Time Bonuses: +{self.total_time_bonus} pts
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

        avg_points = int(self.score / self.attempts) if self.attempts > 0 else 0

        return {
            "success": True,
            "message": f"""
🎮 Game Over!

Final Score: {self.score} points
Answers: {self.attempts}
Average: {avg_points} pts/answer
Max Combo: {self.max_combo}x
Time Bonuses: +{self.total_time_bonus} pts

{'🏆 Speed Demon!' if avg_points >= 40 else '⚡ Quick Thinker!' if avg_points >= 25 else '💪 Keep practicing!'}
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
            "functionality": "speed_translation_game",
            "status": "executed",
            "message": "Use the Streamlit interface to play the speed translation game.",
            "data": {}
        }
