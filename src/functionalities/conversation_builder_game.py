"""
Conversation Builder Game Functionality.
Multi-turn conversation scenarios where users select appropriate responses.
"""
from typing import Dict, Any, Optional, List
from src.functionalities.base import Functionality
from src.ai.datapizza_api import DatapizzaAPI
from src.models.game_models import ConversationExercise


class ConversationBuilderGameFunctionality(Functionality):
    """
    Conversation builder game functionality.
    Users build realistic conversations by selecting appropriate German responses.
    """

    SCENARIOS = [
        "restaurant",
        "shopping",
        "hotel",
        "directions",
        "train_station",
        "cafe",
        "pharmacy",
        "meeting_someone"
    ]

    def __init__(self, api: Optional[DatapizzaAPI] = None):
        """
        Initialize the Conversation Builder Game.

        Args:
            api: DatapizzaAPI instance for conversation generation
        """
        self.api = api
        self.conversation = None
        self.current_turn_index = 0
        self.conversation_history = []
        self.score = 0
        self.attempts = 0
        self.game_active = False
        self.scenario = None
        self.difficulty_range = (1, 5)

    def get_name(self) -> str:
        """Return the name of this functionality."""
        return "conversation_builder_game"

    def start_game(self, difficulty: tuple = (1, 5), **kwargs) -> Dict[str, Any]:
        """
        Start a new conversation builder game.

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
            "message": f"✅ Conversation Builder started! Difficulty: {difficulty[0]}-{difficulty[1]}"
        }

    def next_exercise(self) -> Dict[str, Any]:
        """
        Generate a new conversation scenario.

        Returns:
            Dictionary with the new conversation
        """
        if not self.api:
            return {
                "success": False,
                "error": "API not configured. Use DatapizzaAPI."
            }

        import random
        scenario = random.choice(self.SCENARIOS)

        # Generate conversation using AI
        prompt = f"""
Generate a German conversation exercise for language learners.

Scenario: {scenario}
Difficulty: {self.difficulty_range[0]}-{self.difficulty_range[1]} (1=easiest, 5=hardest)

Create a realistic multi-turn conversation (5-7 exchanges total) between:
- AI character (e.g., waiter, clerk, stranger)
- User (language learner)

Structure:
1. Scenario name and brief description in English
2. List of conversation turns alternating between AI and user
3. For AI turns: provide German text and English translation
4. For user turns: provide:
   - 3 German response options (one correct, two plausible but less appropriate)
   - Correct option index (0-2)
   - Brief explanation why the correct option is best
5. Learning focus (e.g., "formal register", "ordering food", "asking directions")

Guidelines:
- Difficulty 1-2: Simple greetings, basic requests, common phrases
- Difficulty 3-4: More complex interactions, some formal/informal distinctions
- Difficulty 5: Subtle nuances, idiomatic expressions, cultural context
- Make distractors plausible but grammatically or contextually inferior
- Build context through the conversation (later turns reference earlier ones)
- Keep each exchange short and natural

Scenario descriptions by type:
- restaurant: Ordering food, asking about menu, paying bill
- shopping: Asking for items, sizes, prices
- hotel: Checking in, asking about facilities
- directions: Asking how to get somewhere
- train_station: Buying tickets, asking about platforms
- cafe: Ordering drinks, finding a seat
- pharmacy: Asking for medicine, explaining symptoms
- meeting_someone: Introductions, small talk

RESPOND IN ENGLISH for explanations, German for dialogue.
"""

        try:
            response = self.api.client.structured_response(
                input=prompt,
                output_cls=ConversationExercise
            )

            if response.structured_data and len(response.structured_data) > 0:
                conversation_data = response.structured_data[0]

                # Store conversation
                self.conversation = conversation_data
                self.scenario = conversation_data.scenario
                self.current_turn_index = 0
                self.conversation_history = []

                return {
                    "success": True,
                    "sentence": conversation_data.scenario_description,
                    "message": f"New conversation: {conversation_data.scenario}"
                }
            else:
                return {
                    "success": False,
                    "error": "Error generating conversation."
                }
        except Exception as e:
            return {
                "success": False,
                "error": f"Error: {str(e)}"
            }

    def get_current_turn(self) -> Dict[str, Any]:
        """
        Get the current conversation turn.

        Returns:
            Dictionary with current turn information
        """
        if not self.conversation or self.current_turn_index >= len(self.conversation.turns):
            return {
                "success": False,
                "completed": True,
                "message": "Conversation completed!"
            }

        turn = self.conversation.turns[self.current_turn_index]

        return {
            "success": True,
            "completed": False,
            "turn": turn,
            "turn_index": self.current_turn_index,
            "total_turns": len(self.conversation.turns),
            "history": self.conversation_history
        }

    def select_response(self, option_index: int) -> Dict[str, Any]:
        """
        Process user's response selection.

        Args:
            option_index: Index of selected option (0-2)

        Returns:
            Dictionary with validation results
        """
        if not self.conversation or self.current_turn_index >= len(self.conversation.turns):
            return {
                "success": False,
                "error": "No active conversation."
            }

        turn = self.conversation.turns[self.current_turn_index]

        # Check if this is a user turn
        if turn.speaker != "user":
            return {
                "success": False,
                "error": "Current turn is not a user turn."
            }

        self.attempts += 1

        is_correct = option_index == turn.correct_option_index
        selected_text = turn.options[option_index] if 0 <= option_index < len(turn.options) else "Invalid"

        if is_correct:
            self.score += 1

        # Add to history
        self.conversation_history.append({
            "speaker": "user",
            "text": selected_text,
            "translation": turn.english_translation if is_correct else f"(Selected: {selected_text})",
            "correct": is_correct
        })

        # Move to next turn
        self.current_turn_index += 1

        # Check if conversation is complete
        conversation_complete = self.current_turn_index >= len(self.conversation.turns)

        if is_correct:
            percentage = int(self.score / self.attempts * 100) if self.attempts > 0 else 0

            return {
                "success": True,
                "is_correct": True,
                "message": f"✅ Correct!\n\n🇩🇪 **{selected_text}**\n🇬🇧 {turn.english_translation}\n\n💬 **Why:** {turn.explanation}\n\n📊 Score: {self.score}/{self.attempts} ({percentage}%)",
                "conversation_complete": conversation_complete
            }
        else:
            correct_text = turn.options[turn.correct_option_index]
            percentage = int(self.score / self.attempts * 100) if self.attempts > 0 else 0

            return {
                "success": True,
                "is_correct": False,
                "message": f"❌ Not the best choice.\n\nYou selected:\n🇩🇪 **{selected_text}**\n\nBetter option:\n🇩🇪 **{correct_text}**\n🇬🇧 {turn.english_translation}\n\n💬 **Why:** {turn.explanation}\n\n📊 Score: {self.score}/{self.attempts} ({percentage}%)",
                "conversation_complete": conversation_complete,
                "correct_answer": correct_text
            }

    def advance_ai_turn(self) -> Dict[str, Any]:
        """
        Advance past AI turns automatically.

        Returns:
            Dictionary with AI turn information
        """
        if not self.conversation or self.current_turn_index >= len(self.conversation.turns):
            return {
                "success": False,
                "completed": True
            }

        turn = self.conversation.turns[self.current_turn_index]

        if turn.speaker == "ai":
            # Add AI turn to history
            self.conversation_history.append({
                "speaker": "ai",
                "text": turn.german_text,
                "translation": turn.english_translation,
                "correct": True
            })

            # Move to next turn
            self.current_turn_index += 1

            return {
                "success": True,
                "ai_text": turn.german_text,
                "ai_translation": turn.english_translation
            }

        return {"success": False, "message": "Current turn is not an AI turn"}

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
📊 Conversation Progress:

Correct Responses: {self.score}/{self.attempts}
Accuracy: {percentage}%
Scenario: {self.scenario if self.scenario else 'N/A'}
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
                "message": "Game stopped. You didn't complete any conversations yet!"
            }

        percentage = int(self.score / self.attempts * 100)

        return {
            "success": True,
            "message": f"""
🎮 Conversation Complete!

Final Score: {self.score}/{self.attempts} ({percentage}%)

{'🏆 Excellent conversationalist!' if percentage >= 80 else '👍 Good communication!' if percentage >= 60 else '💪 Keep practicing conversations!'}
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
            "functionality": "conversation_builder_game",
            "status": "executed",
            "message": "Use the Streamlit interface to play the conversation builder game.",
            "data": {}
        }
