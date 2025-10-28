"""
Quick test script to verify translation works before running full batch.
"""
import sys
from pathlib import Path
from datapizza.clients.openai_like import OpenAILikeClient
from pydantic import BaseModel, Field

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))


class Translation(BaseModel):
    """Model for translation response."""
    english: str = Field(description="English translation of the Italian word/phrase")


def test_translation():
    """Test translation with a few sample Italian words."""
    print("🧪 Testing translation with Ollama (gemma3:4b)")
    print("=" * 50)
    print()

    # Check Ollama connection
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("✅ Ollama is running")
        else:
            print("❌ Ollama is not responding correctly")
            return
    except Exception as e:
        print(f"❌ Cannot connect to Ollama: {e}")
        print("Please start Ollama with: ollama serve")
        return

    # Initialize client
    client = OpenAILikeClient(
        api_key="",
        model="gemma3:4b",
        base_url="http://localhost:11434/v1",
        system_prompt="You are a professional Italian to English translator. Translate concisely and accurately. Respond with only the English translation, nothing else."
    )

    # Test translations
    test_words = [
        "anno",
        "tempo",
        "persona",
        "giorno",
        "mano",
        "casa",
        "libro",
        "amico"
    ]

    print("\n🔄 Testing translations...")
    print()

    success_count = 0
    fail_count = 0

    for italian in test_words:
        try:
            response = client.structured_response(
                input=f"Translate this Italian word to English: '{italian}'. Provide only the English translation, no explanations.",
                output_cls=Translation
            )

            if response.structured_data and len(response.structured_data) > 0:
                english = response.structured_data[0].english.strip().strip('"').strip("'")
                print(f"  ✓ '{italian}' → '{english}'")
                success_count += 1
            else:
                print(f"  ✗ Failed: '{italian}' (no response data)")
                fail_count += 1

        except Exception as e:
            print(f"  ✗ Error: '{italian}' - {e}")
            fail_count += 1

    # Summary
    print()
    print("=" * 50)
    print(f"Results: {success_count} successful, {fail_count} failed")
    print()

    if success_count >= 6:
        print("✅ Translation is working! Ready to run full script.")
        print("Run: python scripts/translate_csv_data.py")
    elif success_count > 0:
        print("⚠️  Translation partially working. Proceed with caution.")
    else:
        print("❌ Translation not working. Check Ollama setup.")


if __name__ == "__main__":
    test_translation()
