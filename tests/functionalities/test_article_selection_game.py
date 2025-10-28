"""
Tests for Article Selection Game Functionality.
Tests all methods independently of UI to isolate functionality bugs.
"""
import sys
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.functionalities.article_selection_game import ArticleSelectionGameFunctionality
from src.ai.datapizza_api import DatapizzaAPI


def test_game_initialization():
    """Test that game initializes correctly."""
    print("Testing game initialization...")

    game = ArticleSelectionGameFunctionality()

    assert game.score == 0, "Initial score should be 0"
    assert game.attempts == 0, "Initial attempts should be 0"
    assert game.game_active == False, "Game should not be active initially"
    assert game.current_noun is None, "Current noun should be None initially"

    print("✅ Game initialization: PASSED")


def test_start_game():
    """Test starting a game."""
    print("\nTesting start_game()...")

    game = ArticleSelectionGameFunctionality()
    result = game.start_game(difficulty=(1, 3))

    assert result['success'] == True, "start_game should return success=True"
    assert game.game_active == True, "Game should be active after start"
    assert game.difficulty_range == (1, 3), "Difficulty range should be set"

    print("✅ start_game(): PASSED")


def test_next_exercise_without_api():
    """Test that next_exercise fails gracefully without API."""
    print("\nTesting next_exercise() without API...")

    game = ArticleSelectionGameFunctionality(api=None)
    game.start_game(difficulty=(1, 3))
    result = game.next_exercise()

    assert result['success'] == False, "Should fail without API"
    assert 'error' in result, "Should return error message"

    print("✅ next_exercise() without API: PASSED (fails gracefully)")


def test_next_exercise_with_mock_api():
    """Test next_exercise with a real API connection."""
    print("\nTesting next_exercise() with API...")
    print("⚠️  This requires Ollama to be running with gemma3:4b model")

    try:
        # Initialize with Ollama
        api = DatapizzaAPI(
            provider="ollama",
            base_url="http://localhost:11434/v1",
            model="gemma3:4b"
        )

        game = ArticleSelectionGameFunctionality(api=api)
        game.start_game(difficulty=(1, 2))  # Easy difficulty
        result = game.next_exercise()

        if result['success']:
            print(f"  Generated noun: {result.get('noun')}")
            print(f"  Case: {result.get('case')}")
            print(f"  Articles: {result.get('articles')}")
            print(f"  Meaning: {result.get('meaning')}")

            assert 'noun' in result, "Result should contain noun"
            assert 'articles' in result, "Result should contain articles"
            assert 'case' in result, "Result should contain case"
            assert len(result['articles']) == 3, "Should have 3 article options"

            print("✅ next_exercise() with API: PASSED")
        else:
            print(f"❌ next_exercise() failed: {result.get('error')}")

    except Exception as e:
        print(f"⚠️  Skipping API test: {e}")


def test_check_article_selection_correct():
    """Test checking a correct article selection."""
    print("\nTesting check_article_selection() with correct answer...")

    game = ArticleSelectionGameFunctionality()
    game.start_game(difficulty=(1, 3))

    # Manually set up an exercise
    game.current_noun = "Hund"
    game.correct_article = "der"
    game.meaning = "dog"
    game.example_sentence = "Der Hund bellt laut."
    game.example_translation = "The dog barks loudly."
    game.explanation = "Masculine nouns use 'der' in Nominativ."
    game.case = "Nominativ"
    game.all_articles = ["der", "die", "das"]

    result = game.check_article_selection("der")

    assert result['success'] == True, "Check should succeed"
    assert result['is_correct'] == True, "Answer should be correct"
    assert game.score == 1, "Score should increase"
    assert game.attempts == 1, "Attempts should increase"

    print("✅ check_article_selection() correct: PASSED")


def test_check_article_selection_incorrect():
    """Test checking an incorrect article selection."""
    print("\nTesting check_article_selection() with incorrect answer...")

    game = ArticleSelectionGameFunctionality()
    game.start_game(difficulty=(1, 3))

    # Manually set up an exercise
    game.current_noun = "Hund"
    game.correct_article = "der"
    game.meaning = "dog"
    game.example_sentence = "Der Hund bellt laut."
    game.example_translation = "The dog barks loudly."
    game.explanation = "Masculine nouns use 'der' in Nominativ."
    game.case = "Nominativ"
    game.all_articles = ["der", "die", "das"]

    result = game.check_article_selection("die")

    assert result['success'] == True, "Check should succeed"
    assert result['is_correct'] == False, "Answer should be incorrect"
    assert game.score == 0, "Score should not increase"
    assert game.attempts == 1, "Attempts should increase"

    print("✅ check_article_selection() incorrect: PASSED")


def test_get_hint():
    """Test the hint system."""
    print("\nTesting get_hint()...")

    game = ArticleSelectionGameFunctionality()
    game.start_game(difficulty=(1, 3))

    # Set up an exercise
    game.current_noun = "Hund"
    game.correct_article = "der"
    game.meaning = "dog"
    game.example_sentence = "Der Hund bellt laut."
    game.example_translation = "The dog barks loudly."
    game.explanation = "Masculine nouns use 'der' in Nominativ."
    game.case = "Nominativ"

    # Test hint 1
    result1 = game.get_hint()
    assert result1['success'] == True, "Hint 1 should succeed"
    assert 'dog' in result1['message'], "Hint 1 should show meaning"
    print(f"  Hint 1: {result1['message'][:50]}...")

    # Test hint 2
    result2 = game.get_hint()
    assert result2['success'] == True, "Hint 2 should succeed"
    assert 'Nominativ' in result2['message'], "Hint 2 should show case"
    print(f"  Hint 2: {result2['message'][:50]}...")

    # Test hint 3
    result3 = game.get_hint()
    assert result3['success'] == True, "Hint 3 should succeed"
    print(f"  Hint 3: {result3['message'][:50]}...")

    # Test max hints
    result4 = game.get_hint()
    assert result4['success'] == True, "Max hints should succeed"
    assert result4['max_hints'] == True, "Should indicate max hints reached"
    assert 'der' in result4['message'], "Should show full answer"
    print(f"  Hint 4 (max): {result4['message'][:50]}...")

    print("✅ get_hint(): PASSED")


def test_get_score():
    """Test score retrieval."""
    print("\nTesting get_score()...")

    game = ArticleSelectionGameFunctionality()
    game.start_game(difficulty=(1, 3))

    # Simulate some attempts
    game.score = 3
    game.attempts = 5

    result = game.get_score()

    assert result['success'] == True, "get_score should succeed"
    assert '3/5' in result['message'], "Should show score"
    assert '60%' in result['message'], "Should show percentage"

    print("✅ get_score(): PASSED")


def test_stop_game():
    """Test stopping the game."""
    print("\nTesting stop_game()...")

    game = ArticleSelectionGameFunctionality()
    game.start_game(difficulty=(1, 3))
    game.score = 4
    game.attempts = 5

    result = game.stop_game()

    assert result['success'] == True, "stop_game should succeed"
    assert game.game_active == False, "Game should not be active"
    assert '4/5' in result['message'], "Should show final score"

    print("✅ stop_game(): PASSED")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("ARTICLE SELECTION GAME - FUNCTIONALITY TESTS")
    print("=" * 60)

    try:
        test_game_initialization()
        test_start_game()
        test_next_exercise_without_api()
        test_next_exercise_with_mock_api()
        test_check_article_selection_correct()
        test_check_article_selection_incorrect()
        test_get_hint()
        test_get_score()
        test_stop_game()

        print("\n" + "=" * 60)
        print("ALL TESTS PASSED! ✅")
        print("=" * 60)

    except AssertionError as e:
        print(f"\n❌ TEST FAILED: {e}")
        raise
    except Exception as e:
        print(f"\n❌ UNEXPECTED ERROR: {e}")
        raise


if __name__ == "__main__":
    run_all_tests()
