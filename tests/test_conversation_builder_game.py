"""
Unit tests for ConversationBuilderGameFunctionality.
"""
import unittest
from unittest.mock import Mock, patch
from src.functionalities.conversation_builder_game import ConversationBuilderGameFunctionality
from src.models.game_models import ConversationExercise, ConversationTurn


class TestConversationBuilderGameFunctionality(unittest.TestCase):
    """Test suite for ConversationBuilderGameFunctionality."""

    def setUp(self):
        """Set up test fixtures."""
        self.mock_api = Mock()
        self.mock_api.client = Mock()
        self.game = ConversationBuilderGameFunctionality(api=self.mock_api)

    def test_init(self):
        """Test initialization."""
        self.assertIsNotNone(self.game.api)
        self.assertIsNone(self.game.conversation)
        self.assertEqual(self.game.current_turn_index, 0)
        self.assertEqual(self.game.score, 0)
        self.assertFalse(self.game.game_active)

    def test_get_name(self):
        """Test get_name method."""
        self.assertEqual(self.game.get_name(), "conversation_builder_game")

    def test_start_game(self):
        """Test start_game method."""
        result = self.game.start_game(difficulty=(1, 3))

        self.assertTrue(result['success'])
        self.assertEqual(self.game.difficulty_range, (1, 3))
        self.assertTrue(self.game.game_active)

    def test_next_exercise_success(self):
        """Test next_exercise with successful generation."""
        mock_turn1 = ConversationTurn(
            speaker="ai",
            german_text="Guten Tag!",
            english_translation="Good day!",
            options=[],
            correct_option_index=0,
            explanation=""
        )
        mock_turn2 = ConversationTurn(
            speaker="user",
            german_text="",
            english_translation="Good day!",
            options=["Guten Tag!", "Hallo!", "Hi!"],
            correct_option_index=0,
            explanation="Formal greeting."
        )

        mock_conversation = ConversationExercise(
            scenario="restaurant",
            scenario_description="Ordering at a restaurant",
            turns=[mock_turn1, mock_turn2],
            learning_focus="Formal greetings"
        )
        mock_response = Mock()
        mock_response.structured_data = [mock_conversation]
        self.mock_api.client.structured_response.return_value = mock_response

        result = self.game.next_exercise()

        self.assertTrue(result['success'])
        self.assertIsNotNone(self.game.conversation)
        self.assertEqual(self.game.scenario, "restaurant")

    def test_next_exercise_no_api(self):
        """Test next_exercise without API."""
        game_no_api = ConversationBuilderGameFunctionality(api=None)
        result = game_no_api.next_exercise()

        self.assertFalse(result['success'])
        self.assertIn("API not configured", result['error'])

    def test_get_current_turn_no_conversation(self):
        """Test get_current_turn without active conversation."""
        result = self.game.get_current_turn()

        self.assertFalse(result['success'])
        self.assertTrue(result['completed'])

    def test_get_current_turn_with_conversation(self):
        """Test get_current_turn with active conversation."""
        mock_turn = ConversationTurn(
            speaker="ai",
            german_text="Hallo!",
            english_translation="Hello!",
            options=[],
            correct_option_index=0,
            explanation=""
        )
        mock_conversation = ConversationExercise(
            scenario="test",
            scenario_description="Test",
            turns=[mock_turn],
            learning_focus="Test"
        )
        self.game.conversation = mock_conversation
        self.game.current_turn_index = 0

        result = self.game.get_current_turn()

        self.assertTrue(result['success'])
        self.assertFalse(result['completed'])
        self.assertEqual(result['turn_index'], 0)

    def test_select_response_no_conversation(self):
        """Test select_response without active conversation."""
        result = self.game.select_response(0)

        self.assertFalse(result['success'])
        self.assertIn("No active conversation", result['error'])

    def test_select_response_correct(self):
        """Test select_response with correct option."""
        mock_turn = ConversationTurn(
            speaker="user",
            german_text="",
            english_translation="Hello!",
            options=["Hallo!", "Hi!", "Guten Tag!"],
            correct_option_index=0,
            explanation="Casual greeting."
        )
        mock_conversation = ConversationExercise(
            scenario="test",
            scenario_description="Test",
            turns=[mock_turn],
            learning_focus="Test"
        )
        self.game.conversation = mock_conversation
        self.game.current_turn_index = 0

        result = self.game.select_response(0)

        self.assertTrue(result['success'])
        self.assertTrue(result['is_correct'])
        self.assertEqual(self.game.score, 1)

    def test_select_response_incorrect(self):
        """Test select_response with incorrect option."""
        mock_turn = ConversationTurn(
            speaker="user",
            german_text="",
            english_translation="Hello!",
            options=["Hallo!", "Hi!", "Guten Tag!"],
            correct_option_index=0,
            explanation="Casual greeting."
        )
        mock_conversation = ConversationExercise(
            scenario="test",
            scenario_description="Test",
            turns=[mock_turn],
            learning_focus="Test"
        )
        self.game.conversation = mock_conversation
        self.game.current_turn_index = 0

        result = self.game.select_response(1)

        self.assertTrue(result['success'])
        self.assertFalse(result['is_correct'])
        self.assertEqual(self.game.score, 0)

    def test_advance_ai_turn(self):
        """Test advance_ai_turn method."""
        mock_turn = ConversationTurn(
            speaker="ai",
            german_text="Hallo!",
            english_translation="Hello!",
            options=[],
            correct_option_index=0,
            explanation=""
        )
        mock_conversation = ConversationExercise(
            scenario="test",
            scenario_description="Test",
            turns=[mock_turn],
            learning_focus="Test"
        )
        self.game.conversation = mock_conversation
        self.game.current_turn_index = 0

        result = self.game.advance_ai_turn()

        self.assertTrue(result['success'])
        self.assertEqual(self.game.current_turn_index, 1)

    def test_get_score(self):
        """Test get_score method."""
        self.game.score = 4
        self.game.attempts = 5
        self.game.scenario = "restaurant"

        result = self.game.get_score()

        self.assertTrue(result['success'])
        self.assertIn("4/5", result['message'])

    def test_stop_game(self):
        """Test stop_game method."""
        self.game.score = 5
        self.game.attempts = 5

        result = self.game.stop_game()

        self.assertTrue(result['success'])
        self.assertFalse(self.game.game_active)

    def test_execute(self):
        """Test execute method."""
        result = self.game.execute({})

        self.assertEqual(result['functionality'], 'conversation_builder_game')


if __name__ == '__main__':
    unittest.main()
