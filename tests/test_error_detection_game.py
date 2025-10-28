"""
Unit tests for ErrorDetectionGameFunctionality.
"""
import unittest
from unittest.mock import Mock, patch
from src.functionalities.error_detection_game import ErrorDetectionGameFunctionality
from src.models.game_models import ErrorDetectionExercise


class TestErrorDetectionGameFunctionality(unittest.TestCase):
    """Test suite for ErrorDetectionGameFunctionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_api = Mock()
        self.mock_api.client = Mock()
        self.game = ErrorDetectionGameFunctionality(api=self.mock_api)

    def test_init(self):
        """Test initialization."""
        self.assertIsNotNone(self.game.api)
        self.assertIsNotNone(self.game.verb_loader)
        self.assertIsNone(self.game.incorrect_sentence)
        self.assertIsNone(self.game.correct_sentence)
        self.assertEqual(self.game.score, 0)
        self.assertFalse(self.game.game_active)

    def test_get_name(self):
        """Test get_name method."""
        self.assertEqual(self.game.get_name(), "error_detection_game")

    def test_start_game(self):
        """Test start_game method."""
        result = self.game.start_game(difficulty=(1, 3))

        self.assertTrue(result['success'])
        self.assertEqual(self.game.difficulty_range, (1, 3))
        self.assertTrue(self.game.game_active)

    @patch('src.functionalities.error_detection_game.VerbLoader')
    def test_next_exercise_success(self, mock_verb_loader_class):
        """Test next_exercise with successful generation."""
        mock_verb_loader = Mock()
        mock_verb_loader.get_random_verb.return_value = {
            'Verbo': 'gehen',
            'English': 'to go',
            'Frequenza': 2
        }
        self.game.verb_loader = mock_verb_loader

        mock_exercise = ErrorDetectionExercise(
            incorrect_sentence="Ich gehe zum Schule.",
            correct_sentence="Ich gehe zur Schule.",
            error_type="article",
            error_location="zum",
            explanation="Schule is feminine.",
            english_translation="I go to school."
        )
        mock_response = Mock()
        mock_response.structured_data = [mock_exercise]
        self.mock_api.client.structured_response.return_value = mock_response

        result = self.game.next_exercise()

        self.assertTrue(result['success'])
        self.assertEqual(self.game.incorrect_sentence, "Ich gehe zum Schule.")
        self.assertEqual(self.game.correct_sentence, "Ich gehe zur Schule.")

    def test_next_exercise_no_api(self):
        """Test next_exercise without API."""
        game_no_api = ErrorDetectionGameFunctionality(api=None)
        result = game_no_api.next_exercise()

        self.assertFalse(result['success'])
        self.assertIn("API not configured", result['error'])

    def test_check_answer_no_exercise(self):
        """Test check_answer without active exercise."""
        result = self.game.check_answer("Ich gehe zur Schule.")

        self.assertFalse(result['success'])
        self.assertIn("No active exercise", result['error'])

    def test_check_answer_correct(self):
        """Test check_answer with correct answer."""
        self.game.incorrect_sentence = "Ich gehe zum Schule."
        self.game.correct_sentence = "Ich gehe zur Schule."
        self.game.error_type = "article"
        self.game.error_location = "zum"
        self.game.explanation = "Feminine noun."
        self.game.english_translation = "I go to school."

        result = self.game.check_answer("Ich gehe zur Schule.")

        self.assertTrue(result['success'])
        self.assertTrue(result['is_correct'])
        self.assertEqual(self.game.score, 1)

    def test_check_answer_incorrect(self):
        """Test check_answer with incorrect answer."""
        self.game.incorrect_sentence = "Ich gehe zum Schule."
        self.game.correct_sentence = "Ich gehe zur Schule."
        self.game.error_type = "article"
        self.game.error_location = "zum"
        self.game.explanation = "Feminine."
        self.game.english_translation = "I go to school."

        result = self.game.check_answer("Ich gehe zu Schule.")

        self.assertTrue(result['success'])
        self.assertFalse(result['is_correct'])

    def test_get_hint_no_exercise(self):
        """Test get_hint without active exercise."""
        result = self.game.get_hint()

        self.assertFalse(result['success'])
        self.assertIn("No active exercise", result['error'])

    def test_get_hint_progression(self):
        """Test get_hint progression."""
        self.game.incorrect_sentence = "Ich gehe zum Schule."
        self.game.correct_sentence = "Ich gehe zur Schule."
        self.game.error_type = "article"
        self.game.error_location = "zum"
        self.game.english_translation = "I go to school."
        self.game.explanation = "Check article."

        # Hint 1
        result1 = self.game.get_hint()
        self.assertTrue(result1['success'])
        self.assertIn("article", result1['message'])

        # Hint 2
        result2 = self.game.get_hint()
        self.assertTrue(result2['success'])

        # Hint 3
        result3 = self.game.get_hint()
        self.assertTrue(result3['success'])
        self.assertIn("zum", result3['message'])

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

        self.assertEqual(result['functionality'], 'error_detection_game')


if __name__ == '__main__':
    unittest.main()
