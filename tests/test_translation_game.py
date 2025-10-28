"""
Unit tests for TranslationGameFunctionality.
"""
import unittest
from unittest.mock import Mock, MagicMock, patch
from src.functionalities.translation_game import TranslationGameFunctionality
from src.models.game_models import GermanSentence, AnswerValidation


class TestTranslationGameFunctionality(unittest.TestCase):
    """Test suite for TranslationGameFunctionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_api = Mock()
        self.mock_api.client = Mock()
        self.game = TranslationGameFunctionality(api=self.mock_api)

    def test_init(self):
        """Test initialization."""
        self.assertIsNotNone(self.game.api)
        self.assertIsNotNone(self.game.verb_loader)
        self.assertIsNone(self.game.current_sentence)
        self.assertIsNone(self.game.current_translation)
        self.assertEqual(self.game.difficulty_range, (1, 5))
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.attempts, 0)
        self.assertEqual(self.game.tense, "Präsens")
        self.assertFalse(self.game.game_active)
        self.assertEqual(self.game.hint_level, 0)

    def test_get_name(self):
        """Test get_name method."""
        self.assertEqual(self.game.get_name(), "translation_game")

    def test_start_game(self):
        """Test start_game method."""
        result = self.game.start_game(difficulty=(1, 3), tense="Perfekt")

        self.assertTrue(result['success'])
        self.assertEqual(self.game.difficulty_range, (1, 3))
        self.assertEqual(self.game.tense, "Perfekt")
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.attempts, 0)
        self.assertTrue(self.game.game_active)
        self.assertIn("Game started", result['message'])

    def test_start_game_default_params(self):
        """Test start_game with default parameters."""
        result = self.game.start_game()

        self.assertTrue(result['success'])
        self.assertEqual(self.game.difficulty_range, (1, 5))
        self.assertEqual(self.game.tense, "Präsens")

    @patch('src.functionalities.translation_game.VerbLoader')
    def test_next_sentence_success(self, mock_verb_loader_class):
        """Test next_sentence method with successful generation."""
        # Mock verb loader
        mock_verb_loader = Mock()
        mock_verb_loader.get_random_verb.return_value = {
            'Verbo': 'gehen',
            'English': 'to go',
            'Frequenza': 2,
            'Caso': 'N/A'
        }
        self.game.verb_loader = mock_verb_loader

        # Mock API response
        mock_sentence = GermanSentence(
            sentence="Ich gehe zur Schule.",
            translation="I go to school.",
            explanation="Simple present tense with verb gehen."
        )
        mock_response = Mock()
        mock_response.structured_data = [mock_sentence]
        self.mock_api.client.structured_response.return_value = mock_response

        result = self.game.next_sentence()

        self.assertTrue(result['success'])
        self.assertEqual(result['sentence'], "Ich gehe zur Schule.")
        self.assertEqual(self.game.current_sentence, "Ich gehe zur Schule.")
        self.assertEqual(self.game.current_translation, "I go to school.")
        self.assertEqual(self.game.hint_level, 0)

    def test_next_sentence_no_api(self):
        """Test next_sentence without API configured."""
        game_no_api = TranslationGameFunctionality(api=None)
        result = game_no_api.next_sentence()

        self.assertFalse(result['success'])
        self.assertIn("API not configured", result['error'])

    @patch('src.functionalities.translation_game.VerbLoader')
    def test_next_sentence_no_verbs(self, mock_verb_loader_class):
        """Test next_sentence when no verbs are found."""
        mock_verb_loader = Mock()
        mock_verb_loader.get_random_verb.return_value = None
        self.game.verb_loader = mock_verb_loader

        result = self.game.next_sentence()

        self.assertFalse(result['success'])
        self.assertIn("No verbs found", result['error'])

    def test_check_translation_no_sentence(self):
        """Test check_translation without active sentence."""
        result = self.game.check_translation("I go to school")

        self.assertFalse(result['success'])
        self.assertIn("No active sentence", result['error'])

    def test_check_translation_correct(self):
        """Test check_translation with correct answer."""
        self.game.current_sentence = "Ich gehe zur Schule."
        self.game.current_translation = "I go to school."

        # Mock validation
        mock_validation = AnswerValidation(
            is_correct=True,
            feedback="Perfect!",
            correct_answer="I go to school.",
            explanation="Correct translation."
        )
        mock_response = Mock()
        mock_response.structured_data = [mock_validation]
        self.mock_api.client.structured_response.return_value = mock_response

        result = self.game.check_translation("I go to school.")

        self.assertTrue(result['success'])
        self.assertTrue(result['is_correct'])
        self.assertEqual(self.game.score, 1)
        self.assertEqual(self.game.attempts, 1)

    def test_check_translation_incorrect(self):
        """Test check_translation with incorrect answer."""
        self.game.current_sentence = "Ich gehe zur Schule."
        self.game.current_translation = "I go to school."

        # Mock validation
        mock_validation = AnswerValidation(
            is_correct=False,
            feedback="Not quite right.",
            correct_answer="I go to school.",
            explanation="Check the verb conjugation."
        )
        mock_response = Mock()
        mock_response.structured_data = [mock_validation]
        self.mock_api.client.structured_response.return_value = mock_response

        result = self.game.check_translation("I goes to school.")

        self.assertTrue(result['success'])
        self.assertFalse(result['is_correct'])
        self.assertEqual(self.game.score, 0)
        self.assertEqual(self.game.attempts, 1)

    def test_get_hint_no_sentence(self):
        """Test get_hint without active sentence."""
        result = self.game.get_hint()

        self.assertFalse(result['success'])
        self.assertIn("No active sentence", result['error'])

    def test_get_hint_progression(self):
        """Test get_hint progression through hints."""
        self.game.current_sentence = "Ich esse einen Apfel."
        self.game.current_translation = "I eat an apple."
        self.game.current_verb_english = "to eat"

        # Hint 1 - Verb
        result1 = self.game.get_hint()
        self.assertTrue(result1['success'])
        self.assertEqual(self.game.hint_level, 1)
        self.assertIn("Verb", result1['message'])

        # Hint 2 - Nouns
        result2 = self.game.get_hint()
        self.assertTrue(result2['success'])
        self.assertEqual(self.game.hint_level, 2)

        # Hint 3 - Start
        result3 = self.game.get_hint()
        self.assertTrue(result3['success'])
        self.assertEqual(self.game.hint_level, 3)

        # Hint 4 - Full answer
        result4 = self.game.get_hint()
        self.assertTrue(result4['success'])
        self.assertTrue(result4['max_hints'])
        self.assertIn(self.game.current_translation, result4['message'])

    def test_extract_verb_hint(self):
        """Test _extract_verb_hint method."""
        self.game.current_translation = "I eat an apple."
        self.game.current_verb_english = "to eat"

        verb = self.game._extract_verb_hint()
        self.assertIsInstance(verb, str)
        self.assertTrue(len(verb) > 0)

    def test_extract_nouns_from_english(self):
        """Test _extract_nouns_from_english method."""
        self.game.current_translation = "I eat an apple with the fork."

        nouns = self.game._extract_nouns_from_english()
        self.assertIsInstance(nouns, list)
        self.assertIn("apple", nouns)
        self.assertIn("fork", nouns)

    def test_get_score_no_attempts(self):
        """Test get_score with no attempts."""
        result = self.game.get_score()

        self.assertTrue(result['success'])
        self.assertIn("0/0", result['message'])
        self.assertIn("0%", result['message'])

    def test_get_score_with_attempts(self):
        """Test get_score with attempts."""
        self.game.score = 7
        self.game.attempts = 10

        result = self.game.get_score()

        self.assertTrue(result['success'])
        self.assertIn("7/10", result['message'])
        self.assertIn("70%", result['message'])

    def test_stop_game_no_attempts(self):
        """Test stop_game without attempts."""
        result = self.game.stop_game()

        self.assertTrue(result['success'])
        self.assertFalse(self.game.game_active)
        self.assertIn("didn't answer any questions", result['message'])

    def test_stop_game_with_score(self):
        """Test stop_game with score."""
        self.game.score = 8
        self.game.attempts = 10

        result = self.game.stop_game()

        self.assertTrue(result['success'])
        self.assertFalse(self.game.game_active)
        self.assertIn("8/10", result['message'])
        self.assertIn("80%", result['message'])

    def test_execute_start_game(self):
        """Test execute method for starting game."""
        result = self.game.execute({'question': 'start game'})

        self.assertEqual(result['functionality'], 'translation_game')
        self.assertEqual(result['status'], 'executed')
        self.assertTrue(self.game.game_active)

    def test_execute_next_sentence(self):
        """Test execute method for next sentence."""
        # Setup mocks
        mock_verb_loader = Mock()
        mock_verb_loader.get_random_verb.return_value = {
            'Verbo': 'gehen',
            'English': 'to go',
            'Frequenza': 2,
            'Caso': 'N/A'
        }
        self.game.verb_loader = mock_verb_loader

        mock_sentence = GermanSentence(
            sentence="Ich gehe.",
            translation="I go.",
            explanation="Simple."
        )
        mock_response = Mock()
        mock_response.structured_data = [mock_sentence]
        self.mock_api.client.structured_response.return_value = mock_response

        result = self.game.execute({'question': 'next'})

        self.assertEqual(result['functionality'], 'translation_game')
        self.assertEqual(result['status'], 'executed')

    def test_execute_hint(self):
        """Test execute method for hint."""
        self.game.current_sentence = "Test sentence"
        self.game.current_translation = "Test translation"
        self.game.current_verb_english = "test"

        result = self.game.execute({'question': 'hint'})

        self.assertEqual(result['functionality'], 'translation_game')
        self.assertEqual(result['status'], 'executed')

    def test_execute_score(self):
        """Test execute method for score."""
        result = self.game.execute({'question': 'score'})

        self.assertEqual(result['functionality'], 'translation_game')
        self.assertEqual(result['status'], 'executed')

    def test_execute_stop(self):
        """Test execute method for stop."""
        result = self.game.execute({'question': 'stop'})

        self.assertEqual(result['functionality'], 'translation_game')
        self.assertEqual(result['status'], 'executed')
        self.assertFalse(self.game.game_active)

    def test_get_help(self):
        """Test get_help method."""
        help_text = self.game.get_help()

        self.assertIsInstance(help_text, str)
        self.assertIn("Translation Game", help_text)
        self.assertIn("start game", help_text)


if __name__ == '__main__':
    unittest.main()
