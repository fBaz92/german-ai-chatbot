"""
Unit tests for FillBlankGameFunctionality.
"""
import unittest
from unittest.mock import Mock, patch
from src.functionalities.fill_blank_game import FillBlankGameFunctionality
from src.models.game_models import FillInBlankExercise


class TestFillBlankGameFunctionality(unittest.TestCase):
    """Test suite for FillBlankGameFunctionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_api = Mock()
        self.mock_api.client = Mock()
        self.game = FillBlankGameFunctionality(api=self.mock_api)

    def test_init(self):
        """Test initialization."""
        self.assertIsNotNone(self.game.api)
        self.assertIsNotNone(self.game.verb_loader)
        self.assertIsNone(self.game.current_sentence)
        self.assertIsNone(self.game.correct_answer)
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.attempts, 0)
        self.assertFalse(self.game.game_active)

    def test_get_name(self):
        """Test get_name method."""
        self.assertEqual(self.game.get_name(), "fill_blank_game")

    def test_start_game(self):
        """Test start_game method."""
        result = self.game.start_game(difficulty=(2, 4), tense="Perfekt")

        self.assertTrue(result['success'])
        self.assertEqual(self.game.difficulty_range, (2, 4))
        self.assertTrue(self.game.game_active)

    @patch('src.functionalities.fill_blank_game.VerbLoader')
    def test_next_exercise_success(self, mock_verb_loader_class):
        """Test next_exercise with successful generation."""
        mock_verb_loader = Mock()
        mock_verb_loader.get_random_verb.return_value = {
            'Verbo': 'lernen',
            'English': 'to learn',
            'Frequenza': 2
        }
        self.game.verb_loader = mock_verb_loader

        mock_exercise = FillInBlankExercise(
            sentence_with_blank="Ich [BLANK] Deutsch.",
            correct_answer="lerne",
            hint="Present tense verb",
            english_translation="I learn German.",
            explanation="First person singular."
        )
        mock_response = Mock()
        mock_response.structured_data = [mock_exercise]
        self.mock_api.client.structured_response.return_value = mock_response

        result = self.game.next_exercise()

        self.assertTrue(result['success'])
        self.assertEqual(self.game.current_sentence, "Ich [BLANK] Deutsch.")
        self.assertEqual(self.game.correct_answer, "lerne")

    def test_next_exercise_no_api(self):
        """Test next_exercise without API."""
        game_no_api = FillBlankGameFunctionality(api=None)
        result = game_no_api.next_exercise()

        self.assertFalse(result['success'])
        self.assertIn("API not configured", result['error'])

    def test_check_answer_no_exercise(self):
        """Test check_answer without active exercise."""
        result = self.game.check_answer("lerne")

        self.assertFalse(result['success'])
        self.assertIn("No active exercise", result['error'])

    def test_check_answer_correct(self):
        """Test check_answer with correct answer."""
        self.game.current_sentence = "Ich [BLANK] Deutsch."
        self.game.correct_answer = "lerne"
        self.game.english_translation = "I learn German."
        self.game.explanation = "Correct conjugation."

        result = self.game.check_answer("lerne")

        self.assertTrue(result['success'])
        self.assertTrue(result['is_correct'])
        self.assertEqual(self.game.score, 1)

    def test_check_answer_correct_case_insensitive(self):
        """Test check_answer with correct answer but different case."""
        self.game.current_sentence = "Ich [BLANK] Deutsch."
        self.game.correct_answer = "lerne"
        self.game.english_translation = "I learn German."
        self.game.explanation = "Correct."

        result = self.game.check_answer("LERNE")

        self.assertTrue(result['success'])
        self.assertTrue(result['is_correct'])

    def test_check_answer_incorrect(self):
        """Test check_answer with incorrect answer."""
        self.game.current_sentence = "Ich [BLANK] Deutsch."
        self.game.correct_answer = "lerne"
        self.game.english_translation = "I learn German."
        self.game.explanation = "Check conjugation."

        result = self.game.check_answer("lernt")

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
        self.game.current_sentence = "Ich [BLANK] Deutsch."
        self.game.correct_answer = "lerne"
        self.game.hint_text = "Present tense verb"
        self.game.english_translation = "I learn German."

        # Hint 1
        result1 = self.game.get_hint()
        self.assertTrue(result1['success'])
        self.assertIn("Present tense verb", result1['message'])

        # Hint 2
        result2 = self.game.get_hint()
        self.assertTrue(result2['success'])

        # Hint 3
        result3 = self.game.get_hint()
        self.assertTrue(result3['success'])
        self.assertIn("l", result3['message'])

        # Hint 4
        result4 = self.game.get_hint()
        self.assertTrue(result4['success'])

        # Hint 5
        result5 = self.game.get_hint()
        self.assertTrue(result5['success'])
        self.assertTrue(result5['max_hints'])

    def test_get_score(self):
        """Test get_score method."""
        self.game.score = 6
        self.game.attempts = 10

        result = self.game.get_score()

        self.assertTrue(result['success'])
        self.assertIn("6/10", result['message'])

    def test_stop_game(self):
        """Test stop_game method."""
        self.game.score = 7
        self.game.attempts = 10

        result = self.game.stop_game()

        self.assertTrue(result['success'])
        self.assertFalse(self.game.game_active)

    def test_execute(self):
        """Test execute method."""
        result = self.game.execute({})

        self.assertEqual(result['functionality'], 'fill_blank_game')


if __name__ == '__main__':
    unittest.main()
