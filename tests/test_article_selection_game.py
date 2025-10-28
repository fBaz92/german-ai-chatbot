"""
Unit tests for ArticleSelectionGameFunctionality.
"""
import unittest
from unittest.mock import Mock, patch
from src.functionalities.article_selection_game import ArticleSelectionGameFunctionality
from src.models.game_models import ArticleExercise


class TestArticleSelectionGameFunctionality(unittest.TestCase):
    """Test suite for ArticleSelectionGameFunctionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_api = Mock()
        self.mock_api.client = Mock()
        self.game = ArticleSelectionGameFunctionality(api=self.mock_api)

    def test_init(self):
        """Test initialization."""
        self.assertIsNotNone(self.game.api)
        self.assertIsNotNone(self.game.noun_loader)
        self.assertIsNone(self.game.current_noun)
        self.assertIsNone(self.game.correct_article)
        self.assertEqual(self.game.score, 0)
        self.assertFalse(self.game.game_active)

    def test_get_name(self):
        """Test get_name method."""
        self.assertEqual(self.game.get_name(), "article_selection_game")

    def test_start_game(self):
        """Test start_game method."""
        result = self.game.start_game(difficulty=(1, 3))

        self.assertTrue(result['success'])
        self.assertEqual(self.game.difficulty_range, (1, 3))
        self.assertTrue(self.game.game_active)

    @patch('src.functionalities.article_selection_game.NounLoader')
    @patch('src.functionalities.article_selection_game.random.shuffle')
    def test_next_exercise_success(self, mock_shuffle, mock_noun_loader_class):
        """Test next_exercise with successful generation."""
        mock_noun_loader = Mock()
        mock_noun_loader.get_random_noun.return_value = {
            'Sostantivo': 'Hund',
            'Articolo': 'der',
            'English': 'dog',
            'Frequenza': 2
        }
        self.game.noun_loader = mock_noun_loader

        mock_exercise = ArticleExercise(
            noun="Hund",
            correct_article="der",
            case="Nominativ",
            meaning="dog",
            example_sentence="Der Hund bellt.",
            example_translation="The dog barks.",
            distractor_articles=["die", "das"],
            explanation="Masculine noun."
        )
        mock_response = Mock()
        mock_response.structured_data = [mock_exercise]
        self.mock_api.client.structured_response.return_value = mock_response

        result = self.game.next_exercise()

        self.assertTrue(result['success'])
        self.assertEqual(self.game.current_noun, "Hund")
        self.assertEqual(self.game.correct_article, "der")

    def test_next_exercise_no_api(self):
        """Test next_exercise without API."""
        game_no_api = ArticleSelectionGameFunctionality(api=None)
        result = game_no_api.next_exercise()

        self.assertFalse(result['success'])
        self.assertIn("API not configured", result['error'])

    def test_check_article_selection_no_exercise(self):
        """Test check_article_selection without active exercise."""
        result = self.game.check_article_selection("der")

        self.assertFalse(result['success'])
        self.assertIn("No active exercise", result['error'])

    def test_check_article_selection_correct(self):
        """Test check_article_selection with correct answer."""
        self.game.current_noun = "Hund"
        self.game.correct_article = "der"
        self.game.meaning = "dog"
        self.game.explanation = "Masculine."
        self.game.example_sentence = "Der Hund bellt."
        self.game.example_translation = "The dog barks."

        result = self.game.check_article_selection("der")

        self.assertTrue(result['success'])
        self.assertTrue(result['is_correct'])
        self.assertEqual(self.game.score, 1)

    def test_check_article_selection_incorrect(self):
        """Test check_article_selection with incorrect answer."""
        self.game.current_noun = "Hund"
        self.game.correct_article = "der"
        self.game.meaning = "dog"
        self.game.explanation = "Masculine."
        self.game.example_sentence = "Der Hund bellt."
        self.game.example_translation = "The dog barks."

        result = self.game.check_article_selection("die")

        self.assertTrue(result['success'])
        self.assertFalse(result['is_correct'])
        self.assertEqual(self.game.score, 0)

    def test_get_hint_no_exercise(self):
        """Test get_hint without active exercise."""
        result = self.game.get_hint()

        self.assertFalse(result['success'])
        self.assertIn("No active exercise", result['error'])

    def test_get_hint_progression(self):
        """Test get_hint progression."""
        self.game.current_noun = "Hund"
        self.game.correct_article = "der"
        self.game.meaning = "dog"
        self.game.case = "Nominativ"
        self.game.example_sentence = "Der Hund bellt."
        self.game.example_translation = "The dog barks."

        # Hint 1
        result1 = self.game.get_hint()
        self.assertTrue(result1['success'])
        self.assertIn("dog", result1['message'])

        # Hint 2
        result2 = self.game.get_hint()
        self.assertTrue(result2['success'])
        self.assertIn("Nominativ", result2['message'])

        # Hint 3
        result3 = self.game.get_hint()
        self.assertTrue(result3['success'])
        self.assertIn("d", result3['message'])

        # Hint 4
        result4 = self.game.get_hint()
        self.assertTrue(result4['success'])
        self.assertTrue(result4['max_hints'])

    def test_get_score(self):
        """Test get_score method."""
        self.game.score = 8
        self.game.attempts = 10

        result = self.game.get_score()

        self.assertTrue(result['success'])
        self.assertIn("8/10", result['message'])

    def test_stop_game(self):
        """Test stop_game method."""
        self.game.score = 9
        self.game.attempts = 10

        result = self.game.stop_game()

        self.assertTrue(result['success'])
        self.assertFalse(self.game.game_active)

    def test_execute(self):
        """Test execute method."""
        result = self.game.execute({})

        self.assertEqual(result['functionality'], 'article_selection_game')


if __name__ == '__main__':
    unittest.main()
