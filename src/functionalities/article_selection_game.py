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
        self.context_sentence = None
        self.explanation = None
        self.difficulty_range = (1, 5)
        self.score = 0
        self.attempts = 0
        self.game_active = False
        self.hint_level = 0
        self.case = None

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

        # Get random noun
        noun = self.noun_loader.get_random_noun(
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
4. A context sentence showing the noun used with that case
5. 2-3 distractor articles (incorrect but plausible options for that case)
6. Clear explanation of why this article is correct

Case selection by difficulty:
- Difficulty 1-2: Use Nominativ case only
- Difficulty 3-4: Use Akkusativ case (for masculine nouns, article changes from der to den)
- Difficulty 5: Use Dativ or Genitiv case

Article declension reminder:
- Masculine: Nominativ=der, Akkusativ=den, Dativ=dem, Genitiv=des
- Feminine: Nominativ=die, Akkusativ=die, Dativ=der, Genitiv=der
- Neuter: Nominativ=das, Akkusativ=das, Dativ=dem, Genitiv=des

Example if noun is "Hund" (masculine, der):
- For Nominativ: correct_article="der", distractor_articles=["die", "das"]
- For Akkusativ: correct_article="den", distractor_articles=["der", "dem"]
- For Dativ: correct_article="dem", distractor_articles=["den", "der"]

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
                self.context_sentence = exercise_data.context_sentence
                self.explanation = exercise_data.explanation
                self.case = exercise_data.case

                # Combine and shuffle all articles
                self.all_articles = [self.correct_article] + exercise_data.distractor_articles
                random.shuffle(self.all_articles)

                self.hint_level = 0

                return {
                    "success": True,
                    "noun": self.current_noun,
                    "articles": self.all_articles,
                    "case": self.case,
                    "context_sentence": self.context_sentence,
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
                "message": f"✅ Correct! {self.correct_article} {self.current_noun}\n\n{self.explanation}\n\n({self.score}/{self.attempts} = {percentage}%)",
                "correct_answer": f"{self.correct_article} {self.current_noun}"
            }
        else:
            percentage = int(self.score / self.attempts * 100) if self.attempts > 0 else 0

            return {
                "success": True,
                "is_correct": False,
                "message": f"❌ Wrong. You selected '{selected_article}'.\n\n✅ **Correct answer:** {self.correct_article} {self.current_noun}\n\n💬 {self.explanation}\n\n📊 Score: {self.score}/{self.attempts} ({percentage}%)",
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

        # Hint 1: The case
        if self.hint_level >= 1:
            hints.append(f"🔹 **Case:** {self.case}")

        # Hint 2: Context sentence
        if self.hint_level >= 2:
            hints.append(f"🔹 **Context:** {self.context_sentence}")

        # Hint 3: First letter of article
        if self.hint_level >= 3:
            hints.append(f"🔹 **First letter:** {self.correct_article[0]}")

        # Max hints reached - show full answer
        if self.hint_level >= 4:
            return {
                "success": True,
                "message": f"💡 **Full answer:** {self.correct_article} {self.current_noun}",
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
