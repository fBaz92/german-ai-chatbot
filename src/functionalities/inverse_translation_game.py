"""
Translation Game Functionality, from English to German.
Interactive game where users translate English sentences to German.
"""
from typing import Dict, Any, Optional
from src.functionalities.base import Functionality
from src.data.verb_loader import VerbLoader
from src.ai.datapizza_api import DatapizzaAPI
from src.models.game_models import EnglishSentence, AnswerValidation
from src.utils.text_diff import simple_diff


class InverseTranslationGameFunctionality(Functionality):
    """
    Interactive inverse translation game functionality.
    Users translate English sentences to German.
    """
    
    def __init__(self, api: Optional[DatapizzaAPI] = None, csv_path: str = None):
        """
        Initialize the Inverse Translation Game.
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
        self.hint_level = 0  # Track how many hints given for current sentence
        self.focus_item = None
    
    def get_name(self) -> str:
        """Return the name of this functionality."""
        return "inverse_translation_game"

    def start_game(self, difficulty: tuple = (1, 5), tense: str = "Präsens") -> Dict[str, Any]:
        """
        Start a new inverse translation game.
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
        Generate the next sentence for inverse translation.

        Returns:
            Dictionary with the new sentence
        """

        if not self.api:
            return {
                "success": False,
                "error": "API not configured. Use DatapizzaAPI."
            }

        focus_verb = None
        if self.focus_item and self.focus_item.get("item_type") == "verb":
            focus_verb = self.verb_loader.get_verb_by_name(self.focus_item.get("item_key", ""))
            focus_tense = (self.focus_item.get("context") or {}).get("tense")
            if focus_tense:
                self.tense = focus_tense

        verb = focus_verb or self.verb_loader.get_random_verb(
            min_freq=self.difficulty_range[0],
            max_freq=self.difficulty_range[1]
        )
        
        if not verb:
            return {
                "success": False,
                "error": "No verbs found for the selected difficulty."
            }
            
        prompt = f"""
Generate an English sentence using the verb "{verb['English']}" ({verb['Verbo']}) in {self.tense}.
Difficulty level: {verb.get('Frequenza', 3)}/5 (1=easiest, 5=hardest)
Case: {verb.get('Caso', 'N/A')}

Create a natural, everyday sentence that demonstrates proper use of this verb in the specified tense.
Make the sentence appropriate for the difficulty level.
Provide the German translation and a clear explanation.

IMPORTANT: Respond in ENGLISH. The explanation must be in English, not German.
"""

        try:
            response = self.api.client.structured_response(
                input=prompt,
                output_cls=EnglishSentence
            )
            
            if response.structured_data and len(response.structured_data) > 0:
                sentence_data = response.structured_data[0]
                result = {
                    "sentence": sentence_data.sentence,
                    "translation": sentence_data.translation,
                    "explanation": sentence_data.explanation,
                    "verb": verb['English'],
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
            self.current_verb = verb['Verbo']  # Store German verb for hints
            self.current_verb_english = verb['English']  # Store English verb
            self.current_case = verb.get('Caso', 'N/A')  # Store case
            self.hint_level = 0  # Reset hint counter
            self.focus_item = None
            
            return {
                "success": True,
                "sentence": result['sentence'],
                "verb": verb['English'],
                "tense": self.tense,
                "message": f"🇬🇧 {result['sentence']}"
            }
        else:
            return {
                "success": False,
                "error": result.get('explanation', 'Error generating sentence')
            }
        
    def _validate_translation_with_ai(self, user_translation: str) -> Dict[str, Any]:
        """
        Use AI to validate the user's translation.

        Args:
            user_translation: User's translation

        Returns:
            Dictionary with validation results
        """
        validation_prompt = f"""
Question: Translate to German: {self.current_sentence}

User's answer: {user_translation}
Correct answer: {self.current_translation}

Compare the user's answer with the correct answer.

IMPORTANT:
- Be strict in your evaluation
- If the verbs are different, mark as INCORRECT
- If the core meaning changed, mark as INCORRECT
- Grammar and tense must be correct
- Minor variations in word choice are OK if meaning is preserved

RESPOND IN ENGLISH ONLY. All feedback, explanations, and messages must be in English.

Return a JSON object with:
- is_correct: true/false
- feedback: Brief message for the user (IN ENGLISH)
- correct_answer: The correct answer (IN GERMAN)
- explanation: Why it's correct/incorrect (IN ENGLISH)
"""

        try:
            response = self.api.client.structured_response(
                input=validation_prompt,
                output_cls=AnswerValidation
            )

            if response.structured_data and len(response.structured_data) > 0:
                validation = response.structured_data[0]
                return {
                    "is_correct": validation.is_correct,
                    "feedback": validation.feedback,
                    "correct_answer": validation.correct_answer,
                    "explanation": validation.explanation
                }
            else:
                return {
                    "is_correct": False,
                    "feedback": "Could not validate the answer.",
                    "correct_answer": self.current_translation,
                    "explanation": ""
                }
        except Exception as e:
            return {
                "is_correct": False,
                "feedback": f"Validation error: {str(e)}",
                "correct_answer": self.current_translation,
                "explanation": ""
            }

    def check_translation(self, user_translation: str) -> Dict[str, Any]:
        """
        Check if the user's translation is correct.
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

        # Normalize user's answer: add period if missing
        user_translation = user_translation.strip()
        if user_translation and user_translation[-1] not in '.!?':
            user_translation += '.'

        # Validate with AI - pass correct answer explicitly
        validation = self._validate_translation_with_ai(user_translation)
        
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
            
            # Create diff comparison
            diff_text = simple_diff(user_translation, self.current_translation)
            
            return {
                "success": True,
                "is_correct": False,
                "message": f"❌ Wrong.\n\n{diff_text}\n\n✅ **Correct answer:** {self.current_translation}\n\n💬 {validation.get('feedback', '')}\n\n📊 Score: {self.score}/{self.attempts} ({percentage}%)"
            }
        
    def get_hint(self) -> Dict[str, Any]:
        """
        Get progressive hint for the current sentence (EN → GER).
        Hints: 1) Verb, 2) Noun, 3) Case
        
        Returns:
            Dictionary with hint
        """
        if not self.current_translation:
            return {
                "success": False,
                "error": "No active sentence."
            }
        
        self.hint_level += 1
        
        hints = []
        
        # Hint 1: The German verb
        if self.hint_level >= 1:
            hints.append(f"🔹 **Verb:** {self.current_verb}")
        
        # Hint 2: Nouns from the German translation
        if self.hint_level >= 2:
            nouns = self._extract_nouns_from_german()
            if nouns:
                hints.append(f"🔹 **Nouns:** {', '.join(nouns)}")
            else:
                hints.append(f"🔹 **Tip:** No nouns in this sentence")
        
        # Hint 3: The case
        if self.hint_level >= 3:
            if self.current_case and self.current_case != 'N/A':
                hints.append(f"🔹 **Case:** {self.current_case}")
            else:
                hints.append(f"🔹 **Case:** No specific case for this verb")
        
        # Hint 4: First half of answer
        if self.hint_level >= 4:
            words = self.current_translation.split()
            half_words = words[:max(1, len(words) // 2)]
            hints.append(f"🔹 **Start:** {' '.join(half_words)}...")
        
        # Max hints reached
        if self.hint_level >= 5:
            return {
                "success": True,
                "message": f"💡 **Full answer:** {self.current_translation}",
                "max_hints": True
            }
        
        hint_text = "\n".join(hints)
        return {
            "success": True,
            "message": f"💡 **Hint {self.hint_level}/4:**\n\n{hint_text}",
            "max_hints": False
        }
    
    def _extract_nouns_from_german(self) -> list:
        """Extract nouns from German sentence (capitalized words)."""
        words = self.current_translation.split()
        # In German, nouns are capitalized
        nouns = []
        for i, word in enumerate(words):
            # Skip first word and articles
            if i > 0 and word[0].isupper() and word not in ['Der', 'Die', 'Das', 'Ein', 'Eine', 'Den', 'Dem', 'Des']:
                # Remove punctuation
                clean_word = word.rstrip('.,!?')
                if clean_word:
                    nouns.append(clean_word)
        return nouns
        
    def get_score(self) -> Dict[str, Any]:
        """
        Get current score.

        Returns:
            Dictionary with the score information
        """
        if self.attempts == 0:
            percentage = 0
        else:
            percentage = int(self.score/self.attempts*100)
            
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
        """
        self.game_active = False
        
        if self.attempts == 0:
            return {
                "success": True,
                "message": "Game stopped. You didn't answer any questions yet!"
            }
        
        percentage = int(self.score/self.attempts*100)
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
                "functionality": "inverse_translation_game",
                "status": "executed",
                "message": result['message'],
                "data": result
            }
            
        # Next sentence
        elif question in ['next', 'new', 'new sentence', 'next sentence']:
            result = self.next_sentence()  
            return {
                "functionality": "inverse_translation_game",
                "status": "executed",
                "message": result.get('message', result.get('error', '')),
                "data": result
            }
            
        # Hint
        elif question in ['hint', 'help me', 'clue']:
            result = self.get_hint()
            return {
                "functionality": "inverse_translation_game",
                "status": "executed",
                "message": result.get('message', result.get('error', '')),
                "data": result
            }
            
        # Score
        elif question in ['score', 'my score', 'points']:
            result = self.get_score()
            return {
                "functionality": "inverse_translation_game",
                "status": "executed",
                "message": result['message'],
                "data": result
            }
            
        # Stop
        elif question in ['stop', 'quit game', 'end game']:
            result = self.stop_game()
            return {
                "functionality": "inverse_translation_game",
                "status": "executed",
                "message": result['message'],
                "data": result
            }
            
        # Assume it's a translation attempt
        elif self.current_sentence:
            result = self.check_translation(question)
            return {
                "functionality": "inverse_translation_game",
                "status": "executed",
                "message": result.get('message', result.get('error', '')),
                "data": result
            }
        
        else:
            return {
                "functionality": "inverse_translation_game",
                "status": "executed",
                "message": """
🎮 Inverse Translation Game

Commands:
  'start game' - Start a new game
  'start game 1 to 2' - Start with specific difficulty
  'next' - Get next sentence
  'hint' - Get a hint
  'score' - See your score

Not sure what to do? Type 'start game' to begin!
""".strip(),
                "data": {}
            }
        
    def get_help(self) -> str:
        """Get help information for this functionality."""
        return """
            🎮 Inverse Translation Game - Interactive English to German translation practice

            How to play:
            1. Type 'start game' to begin
            2. I'll show you an English sentence
            3. Type your German translation
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
            English: "I eat an apple"
            > Ich esse einen Apfel
            ✅ Correct!
        """
