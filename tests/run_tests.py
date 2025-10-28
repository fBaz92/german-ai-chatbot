"""
Test Runner Script
Runs all functionality tests and reports results.
"""
import sys
import importlib
from pathlib import Path

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


def run_test_file(test_module_path):
    """Run a single test file."""
    try:
        # Import the test module
        module = importlib.import_module(test_module_path)

        # Run the run_all_tests function
        if hasattr(module, 'run_all_tests'):
            module.run_all_tests()
            return True
        else:
            print(f"⚠️  No run_all_tests() function found in {test_module_path}")
            return False

    except Exception as e:
        print(f"❌ Error running {test_module_path}: {e}")
        import traceback
        traceback.print_exc()
        return False


def main():
    """Run all test files."""
    print("\n" + "=" * 70)
    print(" GERMAN LEARNING GAMES - FUNCTIONALITY TEST SUITE")
    print("=" * 70)
    print()

    test_files = [
        "tests.functionalities.test_article_selection_game",
        # Add more test files here as they're created
        # "tests.functionalities.test_translation_game",
        # "tests.functionalities.test_verb_conjugation_game",
        # etc.
    ]

    results = {}

    for test_file in test_files:
        print(f"\n📦 Running: {test_file}")
        print("-" * 70)
        success = run_test_file(test_file)
        results[test_file] = success
        print()

    # Summary
    print("\n" + "=" * 70)
    print(" TEST SUMMARY")
    print("=" * 70)

    total = len(results)
    passed = sum(1 for r in results.values() if r)
    failed = total - passed

    for test_file, success in results.items():
        status = "✅ PASSED" if success else "❌ FAILED"
        print(f"{status:12} - {test_file}")

    print()
    print(f"Total: {total} | Passed: {passed} | Failed: {failed}")

    if failed == 0:
        print("\n🎉 ALL TESTS PASSED!")
    else:
        print(f"\n⚠️  {failed} test(s) failed")
        sys.exit(1)


if __name__ == "__main__":
    main()
