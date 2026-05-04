from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import DB_PATH, init_db


def main() -> None:
    """Delete the local SQLite DB file and recreate an empty schema."""
    db_path = PROJECT_ROOT / DB_PATH

    if db_path.exists():
        db_path.unlink()
        print(f"Deleted database file: {db_path}")
    else:
        print(f"No database file found at: {db_path}")

    init_db()
    print("Database recreated successfully.")


if __name__ == "__main__":
    main()
