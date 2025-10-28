# 🛠️ Scripts Directory

Utility scripts for data processing and maintenance.

---

## 📋 Available Scripts

### 1. `backup_csv_files.py`
**Purpose:** Create timestamped backups of all CSV data files before making changes.

**Usage:**
```bash
python scripts/backup_csv_files.py
```

**What it does:**
- Creates `data/backups/` directory
- Backs up `nomi.csv`, `aggettivi.csv`, `verbi.csv`
- Adds timestamp to backup filenames
- Example: `nomi_20251027_143022.csv`

**When to use:**
- Before running translation script
- Before any manual CSV edits
- Before bulk data updates

---

### 2. `translate_csv_data.py`
**Purpose:** Translate Italian meanings to English and add English column to CSV files.

**Prerequisites:**
- Ollama running locally
- gemma3:4b model downloaded

**Setup:**
```bash
# Install Ollama (if not already installed)
# Visit: https://ollama.ai/

# Start Ollama server
ollama serve

# Download model (in another terminal)
ollama pull gemma3:4b
```

**Usage:**
```bash
# 1. First, backup your data
python scripts/backup_csv_files.py

# 2. Run translation script
python scripts/translate_csv_data.py
```

**What it does:**
1. **Verbs (verbi.csv)**: Verifies English column exists ✅
2. **Nouns (nomi.csv)**:
   - Reads Italian "Significato" column
   - Translates ~1,033 meanings to English using AI
   - Adds "English" column after "Significato"
   - Updates CSV file
3. **Adjectives (aggettivi.csv)**:
   - Reads Italian "Significato" column
   - Translates meanings to English using AI
   - Adds "English" column after "Significato"
   - Updates CSV file

**Progress:**
- Shows real-time translation progress
- Example: `[1/1033] ✓ 'anno' → 'year'`
- Progress updates every 50 items
- Handles errors gracefully (falls back to Italian)

**Result:**
```
Before:
Sostantivo,Articolo,Plurale,Significato,Frequenza
Jahr,das,Jahre,anno,1

After:
Sostantivo,Articolo,Plurale,Significato,English,Frequenza
Jahr,das,Jahre,anno,year,1
```

**Performance:**
- Model: Ollama gemma3:4b (local)
- Cost: FREE (runs on your machine)
- Speed: ~1-2 translations/second (depends on your hardware)
- Total time: ~10-20 minutes for 1,033 nouns + adjectives

---

## 🔧 Future Scripts (Planned)

### `standardize_column_names.py`
- Rename columns to English across all CSV files
- Map: `Sostantivo` → `Noun`, `Aggettivo` → `Adjective`, etc.
- Update all loaders to use new column names

### `validate_csv_data.py`
- Check for missing values
- Verify frequency ranges (1-5)
- Detect duplicate entries
- Validate article genders match noun endings

### `augment_csv_data.py`
- Add more vocabulary from external sources
- Enrich with usage examples
- Add difficulty scoring

---

## 📝 Notes

- Always backup before running modification scripts
- Translation script is idempotent (safe to run multiple times)
- Requires Ollama running locally with gemma3:4b model
- Backups are stored in `data/backups/` (not tracked by git)
- No API keys needed - runs completely offline!

---

## 🐛 Troubleshooting

**"Cannot connect to Ollama"**
- Start Ollama server: `ollama serve`
- Check if running: `curl http://localhost:11434/api/tags`
- Download model if needed: `ollama pull gemma3:4b`

**"CSV file not found"**
- Ensure you're running from project root
- Check `data/` directory exists
- Verify CSV files: `ls data/*.csv`

**Translation fails/slow**
- Ollama uses CPU/GPU - speed depends on hardware
- Close other heavy applications
- Consider using smaller batches if memory issues
- Check Ollama logs: `ollama logs`

**Wrong translations**
- gemma3:4b is optimized for translation
- Occasional errors are expected (script falls back to Italian)
- Review output and fix manually if needed

---

*Last updated: 2025-10-27*
