# 🧪 Testing Guide for German Learning Games

This guide explains how to test game functionalities independently of the UI to isolate bugs.

---

## 🎯 Why Test Functionalities?

**Problem:** When a feature doesn't work (e.g., "Get Hint button"), it's unclear if the issue is:
- ❌ UI layer (button not calling the right method)
- ❌ Functionality layer (hint logic is broken)
- ❌ Integration (wrong method being called)

**Solution:** Test functionalities in isolation to determine where the bug is.

---

## 📁 Test Structure

```
tests/
├── __init__.py
├── run_tests.py                    # Test runner script
├── TESTING_GUIDE.md                # This file
└── functionalities/
    ├── __init__.py
    ├── test_article_selection_game.py
    ├── test_translation_game.py
    ├── test_verb_conjugation_game.py
    └── ... (one per game)
```

---

## 🚀 Running Tests

### Run All Tests
```bash
python tests/run_tests.py
```

### Run Specific Test File
```bash
python tests/functionalities/test_article_selection_game.py
```

### Run With Dependencies
```bash
# Make sure dependencies are installed first
pip install -r requirements.txt

# Make sure Ollama is running (for API tests)
ollama serve

# Then run tests
python tests/run_tests.py
```

---

## 📝 What Each Test Covers

### For Each Game Functionality:

1. **Initialization Test**
   - Game starts with correct default values
   - Score = 0, attempts = 0, game_active = False

2. **start_game() Test**
   - Game activates correctly
   - Difficulty and settings are stored
   - Returns success

3. **next_exercise() / next_sentence() Test**
   - Generates new exercise
   - Returns all required fields
   - Fails gracefully without API

4. **check_answer() / check_translation() Test**
   - Correct answer increases score
   - Incorrect answer doesn't increase score
   - Attempts increase in both cases
   - Returns proper feedback

5. **get_hint() Test**
   - **THIS IS CRITICAL FOR DEBUGGING HINT ISSUES**
   - Hint 1 works
   - Hint 2 works
   - Hint 3 works
   - Max hints shows full answer
   - Returns proper messages

6. **get_score() Test**
   - Returns correct score/attempts
   - Calculates percentage correctly

7. **stop_game() Test**
   - Game deactivates
   - Returns final score

---

## 🔍 Example: Debugging "Get Hint Doesn't Work"

### Step 1: Run Functionality Test
```bash
python tests/functionalities/test_article_selection_game.py
```

### Step 2: Check Test Results

**If get_hint() test PASSES:**
- ✅ Functionality is working
- ❌ Problem is in UI layer
- Check: `src/ui/games/article_selection_ui.py`
- Check: Button is calling `self.state_manager.get_hint()`

**If get_hint() test FAILS:**
- ❌ Functionality is broken
- Check: `src/functionalities/article_selection_game.py`
- Check: `get_hint()` method logic

### Step 3: Look at Test Output

```
Testing get_hint()...
  Hint 1: 🔹 **Meaning:** dog...
  Hint 2: 🔹 **Meaning:** dog
🔹 **Case:** Nominativ...
  Hint 3: 🔹 **Meaning:** dog
🔹 **Case:** Nominativ
🔹 **First letter:** d...
  Hint 4 (max): 💡 **Full answer:** der Hund

📝 **Example:...
✅ get_hint(): PASSED
```

This shows you **exactly** what each hint returns!

---

## 📋 Test Template

Use this template to create tests for new games:

```python
"""
Tests for [Game Name] Functionality.
"""
import sys
from pathlib import Path

sys.path.insert(0, str(Path(__file__).parent.parent.parent))

from src.functionalities.[game_file] import [GameClass]
from src.ai.datapizza_api import DatapizzaAPI


def test_game_initialization():
    """Test that game initializes correctly."""
    print("Testing game initialization...")

    game = [GameClass]()

    assert game.score == 0
    assert game.attempts == 0
    assert game.game_active == False

    print("✅ Game initialization: PASSED")


def test_start_game():
    """Test starting a game."""
    print("\nTesting start_game()...")

    game = [GameClass]()
    result = game.start_game(difficulty=(1, 3))

    assert result['success'] == True
    assert game.game_active == True

    print("✅ start_game(): PASSED")


def test_check_answer_correct():
    """Test checking correct answer."""
    print("\nTesting check_answer() with correct answer...")

    game = [GameClass]()
    game.start_game(difficulty=(1, 3))

    # Set up exercise manually
    game.current_sentence = "Test"
    game.correct_answer = "test"

    result = game.check_answer("test")

    assert result['success'] == True
    assert result['is_correct'] == True
    assert game.score == 1

    print("✅ check_answer() correct: PASSED")


def test_get_hint():
    """Test the hint system - THIS IS KEY!"""
    print("\nTesting get_hint()...")

    game = [GameClass]()
    game.start_game(difficulty=(1, 3))

    # Set up exercise manually
    # ... set all required fields

    # Test each hint level
    result1 = game.get_hint()
    assert result1['success'] == True
    print(f"  Hint 1: {result1['message'][:50]}...")

    result2 = game.get_hint()
    assert result2['success'] == True
    print(f"  Hint 2: {result2['message'][:50]}...")

    print("✅ get_hint(): PASSED")


def run_all_tests():
    """Run all tests."""
    print("=" * 60)
    print("[GAME NAME] - FUNCTIONALITY TESTS")
    print("=" * 60)

    test_game_initialization()
    test_start_game()
    test_check_answer_correct()
    test_get_hint()

    print("\n" + "=" * 60)
    print("ALL TESTS PASSED! ✅")
    print("=" * 60)


if __name__ == "__main__":
    run_all_tests()
```

---

## 🐛 Common Bug Patterns

### Bug: "Get Hint" Button Doesn't Work

**Test:**
```python
def test_get_hint():
    result = game.get_hint()
    print(f"Hint message: {result['message']}")
```

**Possible Issues:**
1. Functionality returns empty message
2. UI not displaying message
3. Button not calling the method
4. Session state not updating

### Bug: Score Not Updating

**Test:**
```python
def test_score_updates():
    game.check_answer("correct")
    assert game.score == 1  # Does this pass?
```

**Possible Issues:**
1. check_answer() not incrementing score
2. UI reading wrong session state variable
3. Score calculation wrong

### Bug: Next Exercise Not Loading

**Test:**
```python
def test_next_exercise():
    result = game.next_exercise()
    print(f"Success: {result['success']}")
    print(f"Fields: {result.keys()}")
```

**Possible Issues:**
1. API call failing
2. Missing required fields in return
3. UI expecting different field names

---

## 📊 Test Coverage Goals

- ✅ **Article Selection**: Fully tested
- ⏳ **Translation Game**: TODO
- ⏳ **Verb Conjugation**: TODO
- ⏳ **Word Selection**: TODO
- ⏳ **Fill-in-the-Blank**: TODO
- ⏳ **Error Detection**: TODO
- ⏳ **Speed Translation**: TODO
- ⏳ **Conversation Builder**: TODO

---

## 💡 Best Practices

1. **Test Without UI First**
   - Isolate functionality bugs
   - Faster to run
   - Easier to debug

2. **Test Happy Path + Error Cases**
   - Correct answers
   - Incorrect answers
   - Edge cases (empty input, max hints, etc.)

3. **Print Intermediate Values**
   - Use `print()` to see what's returned
   - Helps understand the data flow

4. **Mock API Calls When Needed**
   - Don't rely on external APIs for unit tests
   - Test with manually set data

5. **Run Tests Before Commits**
   - Catch regressions early
   - Ensure new features don't break old ones

---

## 🎓 Example Debugging Session

**User reports:** "Hint button in Article Selection does nothing"

### Step 1: Run Test
```bash
python tests/functionalities/test_article_selection_game.py
```

### Step 2: Check Output
```
Testing get_hint()...
  Hint 1: 🔹 **Meaning:** dog...
  Hint 2: 🔹 **Meaning:** dog
🔹 **Case:** Nominativ...
✅ get_hint(): PASSED
```

**Result:** Functionality works! Bug is in UI.

### Step 3: Check UI
Look at `src/ui/games/article_selection_ui.py`:
```python
def render_hint_button(self):
    if st.button("💡 Get Hint"):
        self.state_manager.get_hint()  # Is this being called?
        st.rerun()  # Is rerun happening?
```

### Step 4: Check State Manager
Look at `src/ui/state_manager.py`:
```python
@staticmethod
def get_hint() -> bool:
    if st.session_state.game:
        result = st.session_state.game.get_hint()
        st.session_state.hint_message = result['message']  # Is this set?
        return True
    return False
```

### Step 5: Check UI Display
```python
if st.session_state.hint_message:
    st.info(st.session_state.hint_message)  # Is this shown?
```

**Found bug:** `st.session_state.hint_message` not displayed!

---

## 🚀 Next Steps

1. Create tests for all game functionalities
2. Run tests before any major changes
3. Add CI/CD to run tests automatically
4. Create integration tests for UI layer

---

*Testing infrastructure created: 2025-10-28*
