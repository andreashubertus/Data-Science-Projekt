from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import init_db
from src.database.subscriber import add_subscriber


TEST_SUBSCRIBERS = [
    {
        "email": "Andreas.Hubertus@gmx.de",
        "name": "Andreas",
        "categories": ["POLITICS", "ECONOMY", "TECHNOLOGY", "SPORTS", "CULTURE"],
    },
    {
        "email": "ai.news.summarizer.dhbw@gmail.com",
        "name": "Vitalii",
        "categories": ["POLITICS", "ECONOMY", "TECHNOLOGY", "SPORTS", "CULTURE"],
    }
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
