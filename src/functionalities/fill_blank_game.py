"""
Fill-in-the-Blank Game Functionality.
Interactive game where users fill in missing words in German sentences.
"""
from typing import Dict, Any, Optional
from src.functionalities.base import Functionality
from src.data.verb_loader import VerbLoader
from src.ai.datapizza_api import DatapizzaAPI
from src.models.game_models import FillInBlankExercise


class FillBlankGameFunctionality(Functionality):
    """
    Interactive fill-in-the-blank game functionality.
    Users type the missing word to complete German sentences.
    """

    def __init__(self, api: Optional[DatapizzaAPI] = None, csv_path: str = None):
        """
        Initialize the Fill-in-the-Blank Game.

        Args:
            api: DatapizzaAPI instance for exercise generation
            csv_path: Path to verbs CSV file (optional)
        """
        self.api = api
        self.verb_loader = VerbLoader(csv_path)
        self.current_sentence = None
        self.correct_answer = None
        self.hint_text = None
        self.english_translation = None
        self.explanation = None
        self.difficulty_range = (1, 5)
        self.tense = "Präsens"
        self.score = 0
        self.attempts = 0
        self.game_active = False
        self.hint_level = 0
        self.focus_item = None
        self.current_verb = None

    def get_name(self) -> str:
        """Return the name of this functionality."""
        return "fill_blank_game"

    def start_game(self, difficulty: tuple = (1, 5), tense: str = "Präsens") -> Dict[str, Any]:
        """
        Start a new fill-in-the-blank game.

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
            "message": f"✅ Fill-in-the-Blank Game started! Difficulty: {difficulty[0]}-{difficulty[1]}, Tense: {tense}"
        }

    def next_exercise(self) -> Dict[str, Any]:
        """
        Generate the next fill-in-the-blank exercise.

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

        # Generate fill-in-the-blank exercise using AI
        prompt = f"""
Generate a fill-in-the-blank exercise for German language learners.

Use the verb "{verb['Verbo']}" ({verb['English']}) in {self.tense}.
Difficulty level: {verb.get('Frequenza', 3)}/5 (1=easiest, 5=hardest)

Create an exercise with:
1. A German sentence with [BLANK] replacing ONE key word (verb, noun, or adjective)
2. The correct answer (the missing word)
3. A helpful hint (word type, grammatical info, or context clue)
4. English translation of the complete sentence
5. Explanation of grammar/vocabulary

For difficulty 1-2: Remove simple nouns or common verbs
For difficulty 3-4: Remove verbs in context or articles
For difficulty 5: Remove prepositions, adjective endings, or verb conjugations

Example:
- sentence_with_blank: "Ich [BLANK] jeden Tag Deutsch."
- correct_answer: "lerne"
- hint: "Present tense verb (1st person singular)"
- english_translation: "I learn German every day."
- explanation: "Lerne is the present tense conjugation of lernen for ich"

Make the blank meaningful but solvable with the hint.

RESPOND IN ENGLISH. All hints and explanations must be in English.
"""

        try:
            response = self.api.client.structured_response(
                input=prompt,
                output_cls=FillInBlankExercise
            )

            if response.structured_data and len(response.structured_data) > 0:
                exercise_data = response.structured_data[0]

                # Store data
                self.current_sentence = exercise_data.sentence_with_blank
                self.correct_answer = exercise_data.correct_answer
                self.hint_text = exercise_data.hint
                self.english_translation = exercise_data.english_translation
                self.explanation = exercise_data.explanation
                self.current_verb = verb['Verbo']

                self.hint_level = 0
                self.focus_item = None

                return {
                    "success": True,
                    "sentence": self.current_sentence,
                    "hint": self.hint_text,
                    "message": f"Fill in the blank: {self.current_sentence}"
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
        Check if the user's answer is correct.

        Args:
            user_answer: User's answer for the blank

        Returns:
            Dictionary with validation results
        """
        if not self.current_sentence:
            return {
                "success": False,
                "error": "No active exercise."
            }

        self.attempts += 1

        # Normalize for comparison (lowercase, strip whitespace)
        user_normalized = user_answer.strip().lower()
        correct_normalized = self.correct_answer.strip().lower()

        # Check if answer is correct (allow minor variations)
        is_correct = user_normalized == correct_normalized

        if is_correct:
            self.score += 1
            percentage = int(self.score / self.attempts * 100)

            # Show completed sentence
            completed_sentence = self.current_sentence.replace("[BLANK]", self.correct_answer)

            return {
                "success": True,
                "is_correct": True,
                "message": f"✅ Correct!\n\n**Complete sentence:** {completed_sentence}\n\n**English:** {self.english_translation}\n\n💬 {self.explanation}\n\n({self.score}/{self.attempts} = {percentage}%)",
                "correct_answer": self.correct_answer
            }
        else:
            percentage = int(self.score / self.attempts * 100) if self.attempts > 0 else 0

            completed_sentence = self.current_sentence.replace("[BLANK]", self.correct_answer)

            return {
                "success": True,
                "is_correct": False,
                "message": f"❌ Wrong. You wrote: '{user_answer}'\n\n✅ **Correct answer:** {self.correct_answer}\n\n**Complete sentence:** {completed_sentence}\n\n**English:** {self.english_translation}\n\n💬 {self.explanation}\n\n📊 Score: {self.score}/{self.attempts} ({percentage}%)",
                "correct_answer": self.correct_answer
            }

    def get_hint(self) -> Dict[str, Any]:
        """
        Get progressive hint for the current exercise.

        Returns:
            Dictionary with hint
        """
        if not self.current_sentence or not self.correct_answer:
            return {
                "success": False,
                "error": "No active exercise."
            }

        self.hint_level += 1

        hints = []

        # Hint 1: Initial hint (word type/context)
        if self.hint_level >= 1:
            hints.append(f"🔹 **Hint:** {self.hint_text}")

        # Hint 2: English translation
        if self.hint_level >= 2:
            hints.append(f"🔹 **English:** {self.english_translation}")

        # Hint 3: First letter
        if self.hint_level >= 3:
            hints.append(f"🔹 **First letter:** {self.correct_answer[0]}")

        # Hint 4: Word length
        if self.hint_level >= 4:
            hints.append(f"🔹 **Length:** {len(self.correct_answer)} letters")

        # Max hints reached - show full answer
        if self.hint_level >= 5:
            return {
                "success": True,
                "message": f"💡 **Full answer:** {self.correct_answer}",
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
        return {
            "functionality": "fill_blank_game",
            "status": "executed",
            "message": "Use the Streamlit interface to play the fill-in-the-blank game.",
            "data": {}
        }
