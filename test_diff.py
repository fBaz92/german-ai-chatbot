#!/usr/bin/env python3
"""
Test the text diff highlighting feature.
"""
from src.utils.text_diff import simple_diff, highlight_differences

print("=" * 60)
print("  Testing Text Diff Highlighting")
print("=" * 60)
print()

# Test cases
tests = [
    ("I have my homework", "I have done my homework"),
    ("Der Hund läuft", "Der Hund läuft schnell"),
    ("Ich esse einen Apfel", "Ich esse eine Banane"),
    ("The cat sleeps", "The dog sleeps"),
]

for i, (user, correct) in enumerate(tests, 1):
    print(f"Test {i}:")
    print(f"  User:    {user}")
    print(f"  Correct: {correct}")
    print()
    
    user_hl, correct_hl = highlight_differences(user, correct)
    
    print("  Highlighted:")
    print(f"  User:    {user_hl}")
    print(f"  Correct: {correct_hl}")
    print()
    
    print("  Full diff output:")
    diff = simple_diff(user, correct)
    print(diff)
    print()
    print("-" * 60)
    print()

print("✅ Tests complete!")
print()
print("In Streamlit, the **bold** text will show differences")
print("and ~~strikethrough~~ shows removed words.")

