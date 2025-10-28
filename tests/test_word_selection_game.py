"""
Unit tests for WordSelectionGameFunctionality.
"""
import unittest
from unittest.mock import Mock, patch
from src.functionalities.word_selection_game import WordSelectionGameFunctionality
from src.models.game_models import WordSelectionExercise


class TestWordSelectionGameFunctionality(unittest.TestCase):
    """Test suite for WordSelectionGameFunctionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_api = Mock()
        self.mock_api.client = Mock()
        self.game = WordSelectionGameFunctionality(api=self.mock_api)

    def test_init(self):
        """Test initialization."""
        self.assertIsNotNone(self.game.api)
        self.assertIsNotNone(self.game.verb_loader)
        self.assertIsNone(self.game.current_english_sentence)
        self.assertEqual(self.game.correct_words, [])
        self.assertEqual(self.game.all_words, [])
        self.assertEqual(self.game.difficulty_range, (1, 5))
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.attempts, 0)
        self.assertFalse(self.game.game_active)

    def test_get_name(self):
        """Test get_name method."""
        self.assertEqual(self.game.get_name(), "word_selection_game")

    def test_start_game(self):
        """Test start_game method."""
        result = self.game.start_game(difficulty=(1, 3), tense="Perfekt")

        self.assertTrue(result['success'])
        self.assertEqual(self.game.difficulty_range, (1, 3))
        self.assertEqual(self.game.tense, "Perfekt")
        self.assertTrue(self.game.game_active)

    @patch('src.functionalities.word_selection_game.VerbLoader')
    def test_next_sentence_success(self, mock_verb_loader_class):
        """Test next_sentence with successful generation."""
        mock_verb_loader = Mock()
        mock_verb_loader.get_random_verb.return_value = {
            'Verbo': 'essen',
            'English': 'to eat',
            'Frequenza': 2
        }
        self.game.verb_loader = mock_verb_loader

        mock_exercise = WordSelectionExercise(
            english_sentence="I eat an apple.",
            correct_words=["Ich", "esse", "einen", "Apfel"],
            distractor_words=["isst", "der", "Äpfel"],
            explanation="Using accusative case."
        )
        mock_response = Mock()
        mock_response.structured_data = [mock_exercise]
        self.mock_api.client.structured_response.return_value = mock_response

        result = self.game.next_sentence()

        self.assertTrue(result['success'])
        self.assertEqual(self.game.current_english_sentence, "I eat an apple.")
        self.assertEqual(self.game.correct_words, ["Ich", "esse", "einen", "Apfel"])
        self.assertTrue(len(self.game.all_words) > 4)  # correct + distractors

    def test_next_sentence_no_api(self):
        """Test next_sentence without API."""
        game_no_api = WordSelectionGameFunctionality(api=None)
        result = game_no_api.next_sentence()

        self.assertFalse(result['success'])
        self.assertIn("API not configured", result['error'])

    def test_check_word_selection_no_sentence(self):
        """Test check_word_selection without active sentence."""
        result = self.game.check_word_selection(["Ich", "gehe"])

        self.assertFalse(result['success'])
        self.assertIn("No active sentence", result['error'])

    def test_check_word_selection_correct(self):
        """Test check_word_selection with correct selection."""
        self.game.current_english_sentence = "I go."
        self.game.correct_words = ["Ich", "gehe"]

        result = self.game.check_word_selection(["Ich", "gehe"])

        self.assertTrue(result['success'])
        self.assertTrue(result['is_correct'])
        self.assertEqual(self.game.score, 1)
        self.assertEqual(self.game.attempts, 1)

    def test_check_word_selection_wrong_order(self):
        """Test check_word_selection with wrong order."""
        self.game.current_english_sentence = "I go."
        self.game.correct_words = ["Ich", "gehe"]
        self.game.explanation = "Simple present."

        result = self.game.check_word_selection(["gehe", "Ich"])

        self.assertTrue(result['success'])
        self.assertFalse(result['is_correct'])
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.attempts, 1)
        self.assertIn("order is wrong", result['message'])

    def test_check_word_selection_wrong_words(self):
        """Test check_word_selection with wrong words."""
        self.game.current_english_sentence = "I go."
        self.game.correct_words = ["Ich", "gehe"]
        self.game.explanation = "Simple present."

        result = self.game.check_word_selection(["Ich", "gehst"])

        self.assertTrue(result['success'])
        self.assertFalse(result['is_correct'])
        self.assertIn("Wrong words", result['message'])

    def test_get_hint_no_sentence(self):
        """Test get_hint without active sentence."""
        result = self.game.get_hint()

        self.assertFalse(result['success'])
        self.assertIn("No active sentence", result['error'])

    def test_get_hint_progression(self):
        """Test get_hint progression."""
        self.game.current_english_sentence = "I go."
        self.game.correct_words = ["Ich", "gehe", "zur", "Schule"]

        # Hint 1 - Number of words
        result1 = self.game.get_hint()
        self.assertTrue(result1['success'])
        self.assertIn("4", result1['message'])

        # Hint 2 - First word
        result2 = self.game.get_hint()
        self.assertTrue(result2['success'])
        self.assertIn("Ich", result2['message'])

        # Hint 3 - Last word
        result3 = self.game.get_hint()
        self.assertTrue(result3['success'])
        self.assertIn("Schule", result3['message'])

        # Hint 4 - First half
        result4 = self.game.get_hint()
        self.assertTrue(result4['success'])

        # Hint 5 - Full answer
        result5 = self.game.get_hint()
        self.assertTrue(result5['success'])
        self.assertTrue(result5['max_hints'])

    def test_get_score(self):
        """Test get_score method."""
        self.game.score = 7
        self.game.attempts = 10

        result = self.game.get_score()

        self.assertTrue(result['success'])
        self.assertIn("7/10", result['message'])

    def test_stop_game(self):
        """Test stop_game method."""
        self.game.score = 8
        self.game.attempts = 10

        result = self.game.stop_game()

        self.assertTrue(result['success'])
        self.assertFalse(self.game.game_active)
        self.assertIn("8/10", result['message'])

    def test_execute(self):
        """Test execute method."""
        result = self.game.execute({})

        self.assertEqual(result['functionality'], 'word_selection_game')


if __name__ == '__main__':
    unittest.main()
