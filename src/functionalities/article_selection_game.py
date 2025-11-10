"""
Article Selection Game Functionality.
Interactive game where users select the correct German article (der/die/das).
"""
import random
from typing import Dict, Any, Optional
from src.functionalities.base import Functionality
from src.data.noun_loader import NounLoader
from src.ai.datapizza_api import DatapizzaAPI
from src.models.game_models import ArticleExercise


class ArticleSelectionGameFunctionality(Functionality):
    """
    Interactive article selection game functionality.
    Users select the correct German article for nouns in different cases.
    """

    def __init__(self, api: Optional[DatapizzaAPI] = None, csv_path: str = None):
        """
        Initialize the Article Selection Game.

        Args:
            api: DatapizzaAPI instance for exercise generation
            csv_path: Path to nouns CSV file (optional)
        """
        self.api = api
        self.noun_loader = NounLoader(csv_path)
        self.current_noun = None
        self.correct_article = None
        self.all_articles = []
        self.meaning = None
        self.example_sentence = None
        self.example_translation = None
        self.explanation = None
        self.difficulty_range = (1, 5)
        self.score = 0
        self.attempts = 0
        self.game_active = False
        self.hint_level = 0
        self.case = None
        self.focus_item = None

    def get_name(self) -> str:
        """Return the name of this functionality."""
        return "article_selection_game"

    def start_game(self, difficulty: tuple = (1, 5)) -> Dict[str, Any]:
        """
        Start a new article selection game.

        Args:
            difficulty: Tuple of (min_difficulty, max_difficulty)

        Returns:
            Dictionary with game start information
        """
        self.difficulty_range = difficulty
        self.score = 0
        self.attempts = 0
        self.game_active = True

        return {
            "success": True,
            "message": f"✅ Article Selection Game started! Difficulty: {difficulty[0]}-{difficulty[1]}"
        }

    def next_exercise(self) -> Dict[str, Any]:
        """
        Generate the next article exercise.

        Returns:
            Dictionary with the new exercise
        """
        if not self.api:
            return {
                "success": False,
                "error": "API not configured. Use DatapizzaAPI."
            }

        focus_noun = None
        if self.focus_item and self.focus_item.get("item_type") == "noun":
            focus_noun = self.noun_loader.get_noun_by_name(self.focus_item.get("item_key", ""))

        # Get random noun
        noun = focus_noun or self.noun_loader.get_random_noun(
            min_freq=self.difficulty_range[0],
            max_freq=self.difficulty_range[1]
        )

        if not noun:
            return {
                "success": False,
                "error": "No nouns found for the selected difficulty."
            }

        # Generate article exercise using AI with the specific noun
        prompt = f"""
Generate a German article exercise for language learners using this specific noun:

Noun: {noun['Sostantivo']}
Nominativ article: {noun['Articolo']}
Meaning (English): {noun['English']}
Difficulty level: {noun.get('Frequenza', 3)}/5 (1=easiest, 5=hardest)

IMPORTANT: You MUST use the noun "{noun['Sostantivo']}" provided above. Do not invent a different noun.

Create an exercise with:
1. The noun (without article) - MUST BE: {noun['Sostantivo']}
2. The correct article for a specific case based on the noun's gender and the case
3. The grammatical case (Nominativ/Akkusativ/Dativ/Genitiv)
4. The meaning (English translation of the noun)
5. An example German sentence using this noun with the correct article in this specific case
6. English translation of the example sentence
7. 2 distractor articles - MUST BE valid articles for the SAME case but incorrect for this noun's gender
8. Brief grammatical explanation (1 sentence)

Case selection by difficulty:
- Difficulty 1-2: Use Nominativ case only
- Difficulty 3-4: Use Akkusativ case (for masculine nouns, article changes from der to den)
- Difficulty 5: Use Dativ or Genitiv case

Article declension table:
               Masculine   Feminine   Neuter
Nominativ:     der         die        das
Akkusativ:     den         die        das
Dativ:         dem         der        dem
Genitiv:       des         der        des

CRITICAL RULE FOR DISTRACTOR ARTICLES:
- Distractors MUST be other articles from the SAME case, just for different genders
- Example: If testing Akkusativ masculine (correct="den"), distractors MUST be ["die", "das"] (other Akkusativ articles)
- Example: If testing Dativ feminine (correct="der"), distractors MUST be ["dem"] (other Dativ article, noting die→der in Dativ)
- NEVER include articles from different cases as distractors!

Examples if noun is "Hund" (masculine, der):
- For Nominativ: correct_article="der", distractor_articles=["die", "das"]  (all Nominativ)
- For Akkusativ: correct_article="den", distractor_articles=["die", "das"]  (all Akkusativ)
- For Dativ: correct_article="dem", distractor_articles=["der"]  (all Dativ - note: der appears twice in Dativ table)

Examples if noun is "Frau" (feminine, die):
- For Nominativ: correct_article="die", distractor_articles=["der", "das"]  (all Nominativ)
- For Akkusativ: correct_article="die", distractor_articles=["den", "das"]  (all Akkusativ)
- For Dativ: correct_article="der", distractor_articles=["dem"]  (all Dativ)

RESPOND IN ENGLISH. All explanations must be in English.
"""

        try:
            response = self.api.client.structured_response(
                input=prompt,
                output_cls=ArticleExercise
            )

            if response.structured_data and len(response.structured_data) > 0:
                exercise_data = response.structured_data[0]

                # Store data
                self.current_noun = exercise_data.noun
                self.correct_article = exercise_data.correct_article
                self.meaning = exercise_data.meaning
                self.example_sentence = exercise_data.example_sentence
                self.example_translation = exercise_data.example_translation
                self.explanation = exercise_data.explanation
                self.case = exercise_data.case

                # Combine and shuffle all articles
                self.all_articles = [self.correct_article] + exercise_data.distractor_articles
                random.shuffle(self.all_articles)

                self.hint_level = 0
                self.focus_item = None

                return {
                    "success": True,
                    "noun": self.current_noun,
                    "articles": self.all_articles,
                    "case": self.case,
                    "meaning": self.meaning,
                    "example_sentence": self.example_sentence,
                    "message": f"Select the correct article for '{self.current_noun}' ({self.case})"
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

    def check_article_selection(self, selected_article: str) -> Dict[str, Any]:
        """
        Check if the user's article selection is correct.

        Args:
            selected_article: Article selected by user

        Returns:
            Dictionary with validation results
        """
        if not self.current_noun:
            return {
                "success": False,
                "error": "No active exercise."
            }

        self.attempts += 1

        is_correct = selected_article == self.correct_article

        if is_correct:
            self.score += 1
            percentage = int(self.score / self.attempts * 100)
            return {
                "success": True,
                "is_correct": True,
                "message": f"✅ Correct! **{self.correct_article} {self.current_noun}**\n\n📖 **Meaning:** {self.meaning}\n\n💬 **{self.explanation}**\n\n📝 **Example:**\n🇩🇪 {self.example_sentence}\n🇬🇧 {self.example_translation}\n\n📊 Score: {self.score}/{self.attempts} ({percentage}%)",
                "correct_answer": f"{self.correct_article} {self.current_noun}"
            }
        else:
            percentage = int(self.score / self.attempts * 100) if self.attempts > 0 else 0

            return {
                "success": True,
                "is_correct": False,
                "message": f"❌ Wrong. You selected '{selected_article}'.\n\n✅ **Correct answer:** {self.correct_article} {self.current_noun}\n\n📖 **Meaning:** {self.meaning}\n\n💬 **{self.explanation}**\n\n📝 **Example:**\n🇩🇪 {self.example_sentence}\n🇬🇧 {self.example_translation}\n\n📊 Score: {self.score}/{self.attempts} ({percentage}%)",
                "correct_answer": f"{self.correct_article} {self.current_noun}"
            }

    def get_hint(self) -> Dict[str, Any]:
        """
        Get progressive hint for the current exercise.

        Returns:
            Dictionary with hint
        """
        if not self.current_noun or not self.correct_article:
            return {
                "success": False,
                "error": "No active exercise."
            }

        self.hint_level += 1

        hints = []

        # Hint 1: The meaning
        if self.hint_level >= 1:
            hints.append(f"🔹 **Meaning:** {self.meaning}")

        # Hint 2: The case
        if self.hint_level >= 2:
            hints.append(f"🔹 **Case:** {self.case}")

        # Hint 3: First letter of article
        if self.hint_level >= 3:
            hints.append(f"🔹 **First letter:** {self.correct_article[0]}")

        # Max hints reached - show full answer
        if self.hint_level >= 4:
            return {
                "success": True,
                "message": f"💡 **Full answer:** {self.correct_article} {self.current_noun}\n\n📝 **Example:**\n🇩🇪 {self.example_sentence}\n🇬🇧 {self.example_translation}",
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
            "functionality": "article_selection_game",
            "status": "executed",
            "message": "Use the Streamlit interface to play the article selection game.",
            "data": {}
        }
