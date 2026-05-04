from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import init_db
from src.database.subscriber import add_subscriber


TEST_SUBSCRIBERS = [
    {
        "email": "change-me-tech@example.com",
        "name": "Tech Test",
        "categories": ["TECHNOLOGY", "ECONOMY"],
    },
    {
        "email": "change-me-politics@example.com",
        "name": "Politics Test",
        "categories": ["POLITICS"],
    },
    {
        "email": "change-me-culture@example.com",
        "name": "Culture Test",
        "categories": ["CULTURE", "SPORTS"],
    },
]


def main() -> None:
    """Insert a small set of test subscribers for category-based mailing."""
    init_db()

    print("Seeding test subscribers...")
    for subscriber in TEST_SUBSCRIBERS:
        created = add_subscriber(
            subscriber["email"],
            subscriber["name"],
            categories=subscriber["categories"],
        )
        status = "created" if created else "already exists"
        print(
            f"- {subscriber['email']} ({', '.join(subscriber['categories'])}) -> {status}"
        )

    print("\nDone. Replace the example email addresses with real ones before a live SMTP test.")


if __name__ == "__main__":
    main()
