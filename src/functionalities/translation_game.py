"""
Translation Game Functionality.
Interactive game where users translate German sentences to English.
"""
from typing import Dict, Any, Optional
from src.functionalities.base import Functionality
from src.data.verb_loader import VerbLoader
from src.ai.datapizza_api import DatapizzaAPI, GermanSentence


class TranslationGameFunctionality(Functionality):
    """
    Interactive translation game functionality.
    Users translate German sentences and get immediate feedback.
    """
    
    def __init__(self, api: Optional[DatapizzaAPI] = None, csv_path: str = None):
        """
        Initialize the Translation Game.
        
        Args:
            api: DatapizzaAPI instance for sentence generation and validation
            csv_path: Path to verbs CSV file (optional)
        """
        self.api = api
        self.verb_loader = VerbLoader(csv_path)
        self.current_sentence = None
        self.current_translation = None
        self.difficulty_range = (1, 5)  # Default: easy to medium
        self.score = 0
        self.attempts = 0
        self.tense = "Präsens"
        self.game_active = False
    
    def get_name(self) -> str:
        """Return the name of this functionality."""
        return "translation_game"
    
    def start_game(self, difficulty: tuple = (1, 5), tense: str = "Präsens") -> Dict[str, Any]:
        """
        Start a new translation game.
        
        Args:
            difficulty: Tuple of (min_difficulty, max_difficulty)
            tense: Verb tense to practice
            
        Returns:
            Dictionary with game start information
        """
        self.difficulty_range = difficulty
        self.tense = tense
        self.score = 0
        self.attempts = 0
        self.game_active = True
        
        return {
            "success": True,
            "message": f"✅ Game started! Difficulty: {difficulty[0]}-{difficulty[1]}, Tense: {tense}"
        }
    
    def next_sentence(self) -> Dict[str, Any]:
        """
        Generate the next sentence for translation.
        
        Returns:
            Dictionary with the new sentence
        """
        if not self.api:
            return {
                "success": False,
                "error": "API not configured. Use DatapizzaAPI."
            }
        
        # Get random verb
        verb = self.verb_loader.get_random_verb(
            min_freq=self.difficulty_range[0],
            max_freq=self.difficulty_range[1]
        )
        
        if not verb:
            return {
                "success": False,
                "error": "No verbs found for the selected difficulty."
            }
        
        # Generate sentence using generic API with specific prompt
        prompt = f"""
Generate a German sentence using the verb "{verb['Verbo']}" ({verb['English']}) in {self.tense}.
Difficulty level: {verb.get('Frequenza', 3)}/5 (1=easiest, 5=hardest)
Case: {verb.get('Caso', 'N/A')}

Create a natural, everyday sentence that demonstrates proper use of this verb in the specified tense.
Make the sentence appropriate for the difficulty level.
Provide the English translation and a clear explanation.

IMPORTANT: Respond in ENGLISH. The explanation and translation must be in English, not German.
"""
        
        try:
            response = self.api.client.structured_response(
                input=prompt,
                output_cls=GermanSentence
            )
            
            if response.structured_data and len(response.structured_data) > 0:
                sentence_data = response.structured_data[0]
                result = {
                    "sentence": sentence_data.sentence,
                    "translation": sentence_data.translation,
                    "explanation": sentence_data.explanation,
                    "verb": verb['Verbo'],
                    "tense": self.tense,
                    "success": True
                }
            else:
                result = {
                    "success": False,
                    "error": "Error generating sentence."
                }
        except Exception as e:
            result = {
                "success": False,
                "error": f"Error: {str(e)}"
            }
        
        if result.get('success'):
            self.current_sentence = result['sentence']
            self.current_translation = result['translation']
            
            return {
                "success": True,
                "sentence": result['sentence'],
                "verb": verb['Verbo'],
                "tense": self.tense,
                "message": f"🇩🇪 {result['sentence']}"
            }
        else:
            return {
                "success": False,
                "error": result.get('explanation', 'Error generating sentence')
            }
    
    def check_translation(self, user_translation: str) -> Dict[str, Any]:
        """
        Check if the user's translation is correct.
        
        Args:
            user_translation: User's English translation
            
        Returns:
            Dictionary with validation results
        """
        if not self.current_sentence:
            return {
                "success": False,
                "error": "No active sentence. Type 'next' to get a sentence."
            }
        
        if not self.api:
            return {
                "success": False,
                "error": "API not configured."
            }
        
        # Validate with AI - pass correct answer explicitly
        validation = self.api.check_answer(
            question=f"Translate to English: {self.current_sentence}",
            user_answer=user_translation,
            correct_answer=self.current_translation,
            context={
                "task": "translation",
                "source_language": "German",
                "target_language": "English"
            }
        )
        
        self.attempts += 1
        
        if validation.get('is_correct'):
            self.score += 1
            percentage = int(self.score/self.attempts*100)
            return {
                "success": True,
                "is_correct": True,
                "message": f"✅ Correct! ({self.score}/{self.attempts} = {percentage}%)"
            }
        else:
            percentage = int(self.score/self.attempts*100) if self.attempts > 0 else 0
            return {
                "success": True,
                "is_correct": False,
                "message": f"❌ Wrong. Correct: {self.current_translation}\n{validation.get('feedback', '')}\n📊 {self.score}/{self.attempts} ({percentage}%)"
            }
    
    def get_hint(self) -> Dict[str, Any]:
        """
        Get a hint for the current sentence.
        
        Returns:
            Dictionary with hint
        """
        if not self.current_translation:
            return {
                "success": False,
                "error": "No active sentence."
            }
        
        # Give first few words as hint
        words = self.current_translation.split()
        hint_words = words[:max(1, len(words) // 2)]
        hint = " ".join(hint_words)
        
        return {
            "success": True,
            "message": f"💡 Hint: {hint}..."
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
Tense: {self.tense}
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

Type 'start game' to play again!
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
        question = context.get('question', '').lower().strip()
        
        # Start game
        if 'start' in question and 'game' in question:
            # Parse difficulty if specified
            numbers = [int(s) for s in question.split() if s.isdigit()]
            if len(numbers) >= 2:
                difficulty = (numbers[0], numbers[1])
            elif len(numbers) == 1:
                difficulty = (1, numbers[0])
            else:
                difficulty = self.difficulty_range
            
            result = self.start_game(difficulty=difficulty)
            return {
                "functionality": "translation_game",
                "status": "executed",
                "message": result['message'],
                "data": result
            }
        
        # Next sentence
        elif question in ['next', 'new', 'new sentence', 'next sentence']:
            result = self.next_sentence()
            return {
                "functionality": "translation_game",
                "status": "executed",
                "message": result.get('message', result.get('error', '')),
                "data": result
            }
        
        # Hint
        elif question in ['hint', 'help me', 'clue']:
            result = self.get_hint()
            return {
                "functionality": "translation_game",
                "status": "executed",
                "message": result.get('message', result.get('error', '')),
                "data": result
            }
        
        # Score
        elif question in ['score', 'my score', 'points']:
            result = self.get_score()
            return {
                "functionality": "translation_game",
                "status": "executed",
                "message": result['message'],
                "data": result
            }
        
        # Stop
        elif question in ['stop', 'quit game', 'end game']:
            result = self.stop_game()
            return {
                "functionality": "translation_game",
                "status": "executed",
                "message": result['message'],
                "data": result
            }
        
        # Assume it's a translation attempt
        elif self.current_sentence:
            result = self.check_translation(question)
            return {
                "functionality": "translation_game",
                "status": "executed",
                "message": result.get('message', result.get('error', '')),
                "data": result
            }
        
        else:
            return {
                "functionality": "translation_game",
                "status": "executed",
                "message": """
🎮 Translation Game

Commands:
  'start game' - Start a new game
  'start game 1 to 2' - Start with specific difficulty
  'next' - Get next sentence
  'hint' - Get a hint
  'score' - See your score
  'stop' - End the game

Not sure what to do? Type 'start game' to begin!
""".strip(),
                "data": {}
            }
    
    def get_help(self) -> str:
        """Get help information for this functionality."""
        return """
🎮 Translation Game - Interactive German to English translation practice

How to play:
1. Type 'start game' to begin
2. I'll show you a German sentence
3. Type your English translation
4. Get immediate feedback!

Commands:
  'start game' - Start new game (difficulty 1-5)
  'start game 1 to 2' - Start with easy words only
  'start game 3 to 5' - Start with harder words
  'next' - Get next sentence
  'hint' - Get a hint
  'score' - See your current score
  'stop' - End the game

Example:
  > start game
  > next
  German: "Ich esse einen Apfel"
  > I eat an apple
  ✅ Correct!
"""

