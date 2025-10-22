"""
Text comparison and highlighting utilities.
"""
import difflib
from typing import Tuple


def highlight_differences(user_text: str, correct_text: str) -> Tuple[str, str]:
    """
    Highlight differences between user text and correct text.
    
    Args:
        user_text: User's answer
        correct_text: Correct answer
        
    Returns:
        Tuple of (user_highlighted, correct_highlighted) with markdown formatting
    """
    # Tokenize by words
    user_words = user_text.split()
    correct_words = correct_text.split()
    
    # Use SequenceMatcher to find differences
    matcher = difflib.SequenceMatcher(None, user_words, correct_words)
    
    user_result = []
    correct_result = []
    
    for tag, i1, i2, j1, j2 in matcher.get_opcodes():
        if tag == 'equal':
            # Same in both - no highlight
            user_result.extend(user_words[i1:i2])
            correct_result.extend(correct_words[j1:j2])
        elif tag == 'replace':
            # Different words - highlight both
            user_result.extend([f"**~~{word}~~**" for word in user_words[i1:i2]])
            correct_result.extend([f"**{word}**" for word in correct_words[j1:j2]])
        elif tag == 'delete':
            # Word in user but not in correct - strikethrough
            user_result.extend([f"**~~{word}~~**" for word in user_words[i1:i2]])
        elif tag == 'insert':
            # Word in correct but not in user - bold
            correct_result.extend([f"**{word}**" for word in correct_words[j1:j2]])
    
    user_highlighted = ' '.join(user_result)
    correct_highlighted = ' '.join(correct_result)
    
    return user_highlighted, correct_highlighted


def simple_diff(user_text: str, correct_text: str) -> str:
    """
    Create a simple diff display for Streamlit.
    
    Args:
        user_text: User's answer
        correct_text: Correct answer
        
    Returns:
        Formatted markdown string showing the difference
    """
    user_highlighted, correct_highlighted = highlight_differences(user_text, correct_text)
    
    return f"""
**Your answer:**  
{user_highlighted}

**Correct answer:**  
{correct_highlighted}
"""

