"""
Unit tests for VerbConjugationGameFunctionality.
"""
import unittest
from unittest.mock import Mock, patch
from src.functionalities.verb_conjugation_game import VerbConjugationGameFunctionality
from src.models.game_models import VerbConjugationExercise


class TestVerbConjugationGameFunctionality(unittest.TestCase):
    """Test suite for VerbConjugationGameFunctionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_api = Mock()
        self.mock_api.client = Mock()
        self.game = VerbConjugationGameFunctionality(api=self.mock_api)

    def test_init(self):
        """Test initialization."""
        self.assertIsNotNone(self.game.api)
        self.assertIsNotNone(self.game.verb_loader)
        self.assertIsNone(self.game.current_infinitive)
        self.assertIsNone(self.game.correct_conjugation)
        self.assertEqual(self.game.score, 0)
        self.assertFalse(self.game.game_active)

    def test_get_name(self):
        """Test get_name method."""
        self.assertEqual(self.game.get_name(), "verb_conjugation_game")

    def test_start_game(self):
        """Test start_game method."""
        result = self.game.start_game(difficulty=(2, 4), tense="Perfekt")

        self.assertTrue(result['success'])
        self.assertEqual(self.game.difficulty_range, (2, 4))
        self.assertEqual(self.game.selected_tense, "Perfekt")
        self.assertTrue(self.game.game_active)

    @patch('src.functionalities.verb_conjugation_game.VerbLoader')
    @patch('src.functionalities.verb_conjugation_game.random.choice')
    def test_next_exercise_success(self, mock_choice, mock_verb_loader_class):
        """Test next_exercise with successful generation."""
        mock_verb_loader = Mock()
        mock_verb_loader.get_random_verb.return_value = {
            'Infinitiv': 'gehen',
            'English': 'to go',
            'Frequenz': 2
        }
        self.game.verb_loader = mock_verb_loader
        mock_choice.return_value = "ich"

        mock_exercise = VerbConjugationExercise(
            infinitive="gehen",
            english_meaning="to go",
            pronoun="ich",
            tense="Präsens",
            correct_conjugation="gehe",
            example_sentence="Ich gehe nach Hause.",
            example_translation="I go home.",
            explanation="First person singular."
        )
        mock_response = Mock()
        mock_response.structured_data = [mock_exercise]
        self.mock_api.client.structured_response.return_value = mock_response

        result = self.game.next_exercise()

        self.assertTrue(result['success'])
        self.assertEqual(self.game.current_infinitive, "gehen")
        self.assertEqual(self.game.correct_conjugation, "gehe")

    def test_next_exercise_no_api(self):
        """Test next_exercise without API."""
        game_no_api = VerbConjugationGameFunctionality(api=None)
        result = game_no_api.next_exercise()

        self.assertFalse(result['success'])
        self.assertIn("API not configured", result['error'])

    def test_check_translation_no_exercise(self):
        """Test check_translation without active exercise."""
        result = self.game.check_translation("gehe")

        self.assertFalse(result['success'])
        self.assertIn("No active exercise", result['error'])

    def test_check_translation_correct(self):
        """Test check_translation with correct answer."""
        self.game.current_infinitive = "gehen"
        self.game.correct_conjugation = "gehe"
        self.game.english_meaning = "to go"
        self.game.explanation = "Correct."
        self.game.example_sentence = "Ich gehe."
        self.game.example_translation = "I go."

        result = self.game.check_translation("gehe")

        self.assertTrue(result['success'])
        self.assertTrue(result['is_correct'])
        self.assertEqual(self.game.score, 1)

    def test_check_translation_incorrect(self):
        """Test check_translation with incorrect answer."""
        self.game.current_infinitive = "gehen"
        self.game.correct_conjugation = "gehe"
        self.game.english_meaning = "to go"
        self.game.explanation = "Check."
        self.game.example_sentence = "Ich gehe."
        self.game.example_translation = "I go."

        result = self.game.check_translation("gehst")

        self.assertTrue(result['success'])
        self.assertFalse(result['is_correct'])

    def test_get_hint_no_exercise(self):
        """Test get_hint without active exercise."""
        result = self.game.get_hint()

        self.assertFalse(result['success'])
        self.assertIn("No active exercise", result['error'])

    def test_get_hint_progression(self):
        """Test get_hint progression."""
        self.game.current_infinitive = "gehen"
        self.game.correct_conjugation = "gehe"
        self.game.explanation = "First person singular."
        self.game.example_sentence = "Ich gehe."
        self.game.example_translation = "I go."

        # Hint 1
        result1 = self.game.get_hint()
        self.assertTrue(result1['success'])

        # Hint 2
        result2 = self.game.get_hint()
        self.assertTrue(result2['success'])

        # Hint 3
        result3 = self.game.get_hint()
        self.assertTrue(result3['success'])

        # Hint 4
        result4 = self.game.get_hint()
        self.assertTrue(result4['success'])
        self.assertTrue(result4['max_hints'])

    def test_get_score(self):
        """Test get_score method."""
        self.game.score = 9
        self.game.attempts = 10

        result = self.game.get_score()

        self.assertTrue(result['success'])
        self.assertIn("9/10", result['message'])

    def test_stop_game(self):
        """Test stop_game method."""
        self.game.score = 10
        self.game.attempts = 10

        result = self.game.stop_game()

        self.assertTrue(result['success'])
        self.assertFalse(self.game.game_active)

    def test_execute(self):
        """Test execute method."""
        result = self.game.execute({})

        self.assertEqual(result['functionality'], 'verb_conjugation_game')


if __name__ == '__main__':
    unittest.main()
