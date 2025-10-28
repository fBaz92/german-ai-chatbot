"""
Script to backup CSV data files before translation.
"""
import shutil
from pathlib import Path
from datetime import datetime


def backup_csv_files():
    """Create timestamped backups of all CSV files."""
    project_root = Path(__file__).parent.parent
    data_dir = project_root / "data"
    backup_dir = data_dir / "backups"

    # Create backup directory
    backup_dir.mkdir(exist_ok=True)

    # Get timestamp
    timestamp = datetime.now().strftime("%Y%m%d_%H%M%S")

    # Files to backup
    csv_files = ["nomi.csv", "aggettivi.csv", "verbi.csv"]

    print("📦 Creating CSV backups...")
    print(f"Backup directory: {backup_dir}")
    print()

    for csv_file in csv_files:
        source = data_dir / csv_file
        if source.exists():
            backup_name = f"{csv_file.replace('.csv', '')}_{timestamp}.csv"
            destination = backup_dir / backup_name
            shutil.copy2(source, destination)
            print(f"✅ Backed up: {csv_file} → {backup_name}")
        else:
            print(f"⚠️  Not found: {csv_file}")

    print()
    print(f"✅ Backup complete! Files saved to: {backup_dir}")


if __name__ == "__main__":
    backup_csv_files()
