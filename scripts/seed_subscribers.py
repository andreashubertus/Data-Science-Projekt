from pathlib import Path
import sys


PROJECT_ROOT = Path(__file__).resolve().parents[1]
if str(PROJECT_ROOT) not in sys.path:
    sys.path.insert(0, str(PROJECT_ROOT))

from src.database.connection import init_db
from src.database.subscriber import add_subscriber


ALL_CATEGORIES = ["POLITICS", "ECONOMY", "TECHNOLOGY", "SPORTS", "CULTURE"]

TEST_SUBSCRIBERS = [
    {
        "email": "replace-me-1@example.com",
        "name": "Subscriber One",
        "categories": ALL_CATEGORIES,
    },
    {
        "email": "andreas.huberstus@gmx.de",
        "name": "Subscriber Two",
        "categories": ALL_CATEGORIES,
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

    print(
        "\nDone. Replace the placeholder email addresses with real ones "
        "before a live SMTP test."
    )


if __name__ == "__main__":
    main()
