"""
Noun Loader - Load German nouns from CSV file.
"""
import pandas as pd
import random
from pathlib import Path
from typing import Optional, Dict


class NounLoader:
    """
    Load and manage German nouns from CSV file.
    """

    def __init__(self, csv_path: Optional[str] = None):
        """
        Initialize the noun loader.

        Args:
            csv_path: Path to nouns CSV file. If None, uses default path.
        """
        if csv_path is None:
            # Default path relative to project root
            project_root = Path(__file__).parent.parent.parent
            csv_path = project_root / "data" / "nomi.csv"

        self.csv_path = csv_path
        self.nouns_df = None
        self._load_nouns()

    def _load_nouns(self):
        """Load nouns from CSV file."""
        try:
            self.nouns_df = pd.read_csv(self.csv_path)
            print(f"Loaded {len(self.nouns_df)} nouns from {self.csv_path}")
        except FileNotFoundError:
            print(f"Warning: Nouns file not found at {self.csv_path}")
            self.nouns_df = pd.DataFrame()
        except Exception as e:
            print(f"Error loading nouns: {e}")
            self.nouns_df = pd.DataFrame()

    def get_random_noun(self, min_freq: int = 1, max_freq: int = 5) -> Optional[Dict]:
        """
        Get a random noun within frequency range.

        Args:
            min_freq: Minimum frequency (1-5, 1=most common)
            max_freq: Maximum frequency (1-5)

        Returns:
            Dictionary with noun data or None if not found
        """
        if self.nouns_df is None or self.nouns_df.empty:
            return None

        # Filter by frequency
        filtered = self.nouns_df[
            (self.nouns_df['Frequenza'] >= min_freq) &
            (self.nouns_df['Frequenza'] <= max_freq)
        ]

        if filtered.empty:
            # If no nouns in range, use all
            filtered = self.nouns_df

        # Select random noun
        noun_row = filtered.sample(n=1).iloc[0]

        # Prefer English translation, fall back to Italian
        meaning = noun_row.get('English', noun_row.get('Significato', ''))

        return {
            'Sostantivo': noun_row['Sostantivo'],
            'Articolo': noun_row['Articolo'],
            'Plurale': noun_row.get('Plurale', ''),
            'Significato': noun_row.get('Significato', ''),
            'English': meaning,
            'Frequenza': noun_row.get('Frequenza', 3)
        }

    def get_noun_by_name(self, noun: str) -> Optional[Dict]:
        """
        Get a specific noun by name.

        Args:
            noun: Noun to find

        Returns:
            Dictionary with noun data or None if not found
        """
        if self.nouns_df is None or self.nouns_df.empty:
            return None

        result = self.nouns_df[self.nouns_df['Sostantivo'].str.lower() == noun.lower()]

        if result.empty:
            return None

        noun_row = result.iloc[0]

        # Prefer English translation, fall back to Italian
        meaning = noun_row.get('English', noun_row.get('Significato', ''))

        return {
            'Sostantivo': noun_row['Sostantivo'],
            'Articolo': noun_row['Articolo'],
            'Plurale': noun_row.get('Plurale', ''),
            'Significato': noun_row.get('Significato', ''),
            'English': meaning,
            'Frequenza': noun_row.get('Frequenza', 3)
        }

    def get_nouns_by_article(self, article: str, count: int = 10) -> list:
        """
        Get nouns with specific article.

        Args:
            article: Article to filter by (der/die/das)
            count: Number of nouns to return

        Returns:
            List of noun dictionaries
        """
        if self.nouns_df is None or self.nouns_df.empty:
            return []

        filtered = self.nouns_df[self.nouns_df['Articolo'] == article]

        if filtered.empty:
            return []

        # Sample up to 'count' nouns
        sample_size = min(count, len(filtered))
        samples = filtered.sample(n=sample_size)

        return [
            {
                'Sostantivo': row['Sostantivo'],
                'Articolo': row['Articolo'],
                'Plurale': row.get('Plurale', ''),
                'Significato': row.get('Significato', ''),
                'English': row.get('English', row.get('Significato', '')),
                'Frequenza': row.get('Frequenza', 3)
            }
            for _, row in samples.iterrows()
        ]
