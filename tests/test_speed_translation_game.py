"""
Unit tests for SpeedTranslationGameFunctionality.
"""
import unittest
from unittest.mock import Mock, patch
from src.functionalities.speed_translation_game import SpeedTranslationGameFunctionality
from src.models.game_models import SpeedTranslationExercise


class TestSpeedTranslationGameFunctionality(unittest.TestCase):
    """Test suite for SpeedTranslationGameFunctionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_api = Mock()
        self.mock_api.client = Mock()
        self.game = SpeedTranslationGameFunctionality(api=self.mock_api)

    def test_init(self):
        """Test initialization."""
        self.assertIsNotNone(self.game.api)
        self.assertIsNone(self.game.current_phrase)
        self.assertIsNone(self.game.correct_translation)
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.combo, 0)
        self.assertFalse(self.game.game_active)

    def test_get_name(self):
        """Test get_name method."""
        self.assertEqual(self.game.get_name(), "speed_translation_game")

    def test_start_game(self):
        """Test start_game method."""
        result = self.game.start_game(difficulty=(1, 3))

        self.assertTrue(result['success'])
        self.assertEqual(self.game.difficulty_range, (1, 3))
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.combo, 0)
        self.assertTrue(self.game.game_active)

    @patch('src.functionalities.speed_translation_game.time.time')
    def test_next_exercise_success(self, mock_time):
        """Test next_exercise with successful generation."""
        mock_time.return_value = 1000.0

        mock_exercise = SpeedTranslationExercise(
            german_phrase="Hallo",
            english_translation="Hello",
            difficulty=1,
            category="greetings"
        )
        mock_response = Mock()
        mock_response.structured_data = [mock_exercise]
        self.mock_api.client.structured_response.return_value = mock_response

        result = self.game.next_exercise()

        self.assertTrue(result['success'])
        self.assertEqual(self.game.current_phrase, "Hallo")
        self.assertEqual(self.game.correct_translation, "Hello")
        self.assertEqual(self.game.difficulty, 1)
        self.assertEqual(self.game.start_time, 1000.0)

    def test_next_exercise_no_api(self):
        """Test next_exercise without API."""
        game_no_api = SpeedTranslationGameFunctionality(api=None)
        result = game_no_api.next_exercise()

        self.assertFalse(result['success'])
        self.assertIn("API not configured", result['error'])

    def test_check_translation_no_exercise(self):
        """Test check_translation without active exercise."""
        result = self.game.check_translation("Hello")

        self.assertFalse(result['success'])
        self.assertIn("No active exercise", result['error'])

    @patch('src.functionalities.speed_translation_game.time.time')
    def test_check_translation_correct_fast(self, mock_time):
        """Test check_translation with correct fast answer."""
        self.game.current_phrase = "Hallo"
        self.game.correct_translation = "Hello"
        self.game.difficulty = 1
        self.game.time_limit = 15
        self.game.start_time = 1000.0
        mock_time.return_value = 1005.0  # 5 seconds

        result = self.game.check_translation("Hello")

        self.assertTrue(result['success'])
        self.assertTrue(result['is_correct'])
        self.assertGreater(self.game.score, 0)
        self.assertEqual(self.game.combo, 1)

    @patch('src.functionalities.speed_translation_game.time.time')
    def test_check_translation_correct_slow(self, mock_time):
        """Test check_translation with correct slow answer."""
        self.game.current_phrase = "Hallo"
        self.game.correct_translation = "Hello"
        self.game.difficulty = 1
        self.game.time_limit = 15
        self.game.start_time = 1000.0
        mock_time.return_value = 1020.0  # 20 seconds (over limit)

        result = self.game.check_translation("Hello")

        self.assertTrue(result['success'])
        self.assertTrue(result['is_correct'])

    @patch('src.functionalities.speed_translation_game.time.time')
    def test_check_translation_incorrect(self, mock_time):
        """Test check_translation with incorrect answer."""
        self.game.current_phrase = "Hallo"
        self.game.correct_translation = "Hello"
        self.game.difficulty = 1
        self.game.time_limit = 15
        self.game.start_time = 1000.0
        self.game.combo = 3
        mock_time.return_value = 1005.0

        result = self.game.check_translation("Hi")

        self.assertTrue(result['success'])
        self.assertFalse(result['is_correct'])
        self.assertEqual(self.game.combo, 0)  # Reset on wrong answer

    def test_get_hint_no_exercise(self):
        """Test get_hint without active exercise."""
        result = self.game.get_hint()

        self.assertFalse(result['success'])
        self.assertIn("No active exercise", result['error'])

    def test_get_hint_resets_combo(self):
        """Test get_hint resets combo."""
        self.game.current_phrase = "Hallo"
        self.game.correct_translation = "Hello"
        self.game.combo = 5

        result = self.game.get_hint()

        self.assertTrue(result['success'])
        self.assertEqual(self.game.combo, 0)

    def test_get_score(self):
        """Test get_score method."""
        self.game.score = 100
        self.game.attempts = 10
        self.game.max_combo = 5
        self.game.total_time_bonus = 50

        result = self.game.get_score()

        self.assertTrue(result['success'])
        self.assertIn("100", result['message'])

    def test_stop_game(self):
        """Test stop_game method."""
        self.game.score = 200
        self.game.attempts = 15

        result = self.game.stop_game()

        self.assertTrue(result['success'])
        self.assertFalse(self.game.game_active)

    def test_execute(self):
        """Test execute method."""
        result = self.game.execute({})

        self.assertEqual(result['functionality'], 'speed_translation_game')


if __name__ == '__main__':
    unittest.main()
