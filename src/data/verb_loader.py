"""
Helper module for loading and filtering German verbs from CSV data.
"""
import csv
import random
from pathlib import Path
from typing import List, Dict, Optional


class VerbLoader:
    """Load and filter German verbs from CSV file."""
    
    def __init__(self, csv_path: str = None):
        """
        Initialize the VerbLoader.
        
        Args:
            csv_path: Path to the verbs CSV file. If None, uses default path.
        """
        if csv_path is None:
            # Default path relative to project root
            base_path = Path(__file__).parent.parent.parent
            csv_path = base_path / "data" / "verbi.csv"
        
        self.csv_path = Path(csv_path)
        self.verbs: List[Dict[str, str]] = []
        self._load_verbs()
    
    def _load_verbs(self):
        """Load verbs from CSV file."""
        try:
            with open(self.csv_path, 'r', encoding='utf-8') as file:
                reader = csv.DictReader(file)
                self.verbs = list(reader)
        except FileNotFoundError:
            print(f"Warning: CSV file not found at {self.csv_path}")
            self.verbs = []
    
    def get_verbs_by_difficulty(self, min_freq: int = 1, max_freq: int = 5) -> List[Dict[str, str]]:
        """
        Get verbs filtered by difficulty level (frequency).
        
        Args:
            min_freq: Minimum frequency (1 = easiest)
            max_freq: Maximum frequency (5 = hardest)
            
        Returns:
            List of verb dictionaries matching the criteria
        """
        return [
            verb for verb in self.verbs
            if min_freq <= int(verb.get('Frequenza', 5)) <= max_freq
        ]
    
    def get_random_verb(self, min_freq: int = 1, max_freq: int = 5) -> Optional[Dict[str, str]]:
        """
        Get a random verb within the specified difficulty range.
        
        Args:
            min_freq: Minimum frequency (1 = easiest)
            max_freq: Maximum frequency (5 = hardest)
            
        Returns:
            Random verb dictionary or None if no verbs found
        """
        filtered_verbs = self.get_verbs_by_difficulty(min_freq, max_freq)
        if not filtered_verbs:
            return None
        return random.choice(filtered_verbs)
    
    def get_verb_by_name(self, verb_name: str) -> Optional[Dict[str, str]]:
        """
        Get a specific verb by its German name.
        
        Args:
            verb_name: German verb (infinitive form)
            
        Returns:
            Verb dictionary or None if not found
        """
        for verb in self.verbs:
            if verb.get('Verbo', '').lower() == verb_name.lower():
                return verb
        return None
    
    def get_verb_info(self, verb: Dict[str, str]) -> str:
        """
        Get formatted information about a verb.
        
        Args:
            verb: Verb dictionary
            
        Returns:
            Formatted string with verb information
        """
        return f"""
Verb: {verb.get('Verbo', 'N/A')}
Meaning: {verb.get('English', 'N/A')}
Regular: {verb.get('Regolare', 'N/A')}
Präteritum: {verb.get('Präteritum', 'N/A')}
Past Participle: {verb.get('Participio passato', 'N/A')}
Case: {verb.get('Caso', 'N/A')}
Difficulty: {verb.get('Frequenza', 'N/A')}/5
        """.strip()

