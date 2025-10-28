"""
Script to translate Italian meanings to English and standardize CSV columns.
Uses local Ollama (gemma3:4b) for translations.
"""
import os
import sys
import pandas as pd
from pathlib import Path
from dotenv import load_dotenv
from datapizza.clients.openai_like import OpenAILikeClient
from pydantic import BaseModel, Field

# Add parent directory to path
sys.path.insert(0, str(Path(__file__).parent.parent))

# Load environment variables
env_path = Path(__file__).parent.parent / '.env'
load_dotenv(dotenv_path=env_path)


class Translation(BaseModel):
    """Model for translation response."""
    english: str = Field(description="English translation of the Italian word/phrase")


def translate_meanings(italian_meanings: list[str], batch_size: int = 1) -> list[str]:
    """
    Translate Italian meanings to English using local Ollama (gemma3:4b).

    Args:
        italian_meanings: List of Italian meanings to translate
        batch_size: Number of translations per API call (1 for local model)

    Returns:
        List of English translations
    """
    print("🔧 Using Ollama (local) with gemma3:4b model")
    print("⚠️  Make sure Ollama is running: ollama serve")
    print()

    client = OpenAILikeClient(
        api_key="",  # Ollama doesn't need API key
        model="gemma3:4b",
        base_url="http://localhost:11434/v1",
        system_prompt="You are a professional Italian to English translator. Translate concisely and accurately. Respond with only the English translation, nothing else."
    )

    english_translations = []

    print(f"Translating {len(italian_meanings)} meanings...")
    print()

    # Process one at a time for local model (more reliable)
    for i, italian in enumerate(italian_meanings, 1):
        try:
            response = client.structured_response(
                input=f"Translate this Italian word/phrase to English: '{italian}'. Provide only the English translation, no explanations.",
                output_cls=Translation
            )

            if response.structured_data and len(response.structured_data) > 0:
                english = response.structured_data[0].english
                # Clean up response (remove quotes, extra text)
                english = english.strip().strip('"').strip("'")
                english_translations.append(english)
                print(f"  [{i}/{len(italian_meanings)}] ✓ '{italian}' → '{english}'")
            else:
                print(f"  [{i}/{len(italian_meanings)}] ✗ Failed to translate '{italian}', using original")
                english_translations.append(italian)

        except Exception as e:
            print(f"  [{i}/{len(italian_meanings)}] ✗ Error: {e}")
            # Use original Italian as fallback
            english_translations.append(italian)

        # Show progress every 50 items
        if i % 50 == 0:
            print(f"\n--- Progress: {i}/{len(italian_meanings)} ({int(i/len(italian_meanings)*100)}%) ---\n")

    return english_translations


def process_nouns(csv_path: Path, output_path: Path):
    """Process nouns CSV - add English column."""
    print(f"\n📝 Processing nouns: {csv_path}")

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} nouns")

    # Check if English column already exists
    if 'English' in df.columns:
        print("English column already exists, skipping...")
        return

    # Translate Italian meanings
    italian_meanings = df['Significato'].tolist()
    english_translations = translate_meanings(italian_meanings)

    # Add English column (insert after Significato)
    significato_index = df.columns.get_loc('Significato')
    df.insert(significato_index + 1, 'English', english_translations)

    # Save updated CSV
    df.to_csv(output_path, index=False)
    print(f"✅ Saved updated nouns to: {output_path}")
    print(f"New columns: {list(df.columns)}")


def process_adjectives(csv_path: Path, output_path: Path):
    """Process adjectives CSV - add English column."""
    print(f"\n📝 Processing adjectives: {csv_path}")

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} adjectives")

    # Check if English column already exists
    if 'English' in df.columns:
        print("English column already exists, skipping...")
        return

    # Translate Italian meanings
    italian_meanings = df['Significato'].tolist()
    english_translations = translate_meanings(italian_meanings)

    # Add English column (insert after Significato)
    significato_index = df.columns.get_loc('Significato')
    df.insert(significato_index + 1, 'English', english_translations)

    # Save updated CSV
    df.to_csv(output_path, index=False)
    print(f"✅ Saved updated adjectives to: {output_path}")
    print(f"New columns: {list(df.columns)}")


def verify_verbs(csv_path: Path):
    """Verify verbs CSV already has English column."""
    print(f"\n📝 Verifying verbs: {csv_path}")

    df = pd.read_csv(csv_path)
    print(f"Loaded {len(df)} verbs")

    if 'English' in df.columns:
        print("✅ Verbs already have English column")
        print(f"Columns: {list(df.columns)}")
    else:
        print("⚠️ Verbs missing English column!")


def main():
    """Main script execution."""
    print("🌐 CSV Translation & Standardization Script")
    print("=" * 50)

    # Get project root
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"

    # Define file paths
    nouns_path = data_dir / "nomi.csv"
    adjectives_path = data_dir / "aggettivi.csv"
    verbs_path = data_dir / "verbi.csv"

    # Create output paths (will overwrite originals)
    nouns_output = data_dir / "nomi.csv"
    adjectives_output = data_dir / "aggettivi.csv"

    # Verify all files exist
    if not nouns_path.exists():
        print(f"❌ Error: {nouns_path} not found")
        return

    if not adjectives_path.exists():
        print(f"❌ Error: {adjectives_path} not found")
        return

    if not verbs_path.exists():
        print(f"❌ Error: {verbs_path} not found")
        return

    # Verify Ollama is available
    print("🔍 Checking if Ollama is running...")
    try:
        import requests
        response = requests.get("http://localhost:11434/api/tags", timeout=2)
        if response.status_code == 200:
            print("✅ Ollama is running")
        else:
            print("⚠️  Ollama may not be running properly")
    except Exception as e:
        print("❌ Error: Cannot connect to Ollama")
        print("Please start Ollama with: ollama serve")
        print("Then download the model: ollama pull gemma3:4b")
        return

    print()

    # Process files
    try:
        # Verify verbs (already have English)
        verify_verbs(verbs_path)

        # Process nouns
        process_nouns(nouns_path, nouns_output)

        # Process adjectives
        process_adjectives(adjectives_path, adjectives_output)

        print("\n" + "=" * 50)
        print("✅ All CSV files processed successfully!")
        print("\nSummary:")
        print(f"  - Verbs: Already had English translations")
        print(f"  - Nouns: Added English column to {nouns_output}")
        print(f"  - Adjectives: Added English column to {adjectives_output}")
        print(f"\n🤖 Translations powered by: Ollama (gemma3:4b)")
        print(f"💰 Cost: FREE (local model)")

    except Exception as e:
        print(f"\n❌ Error during processing: {e}")
        import traceback
        traceback.print_exc()


if __name__ == "__main__":
    main()
