from models import Subscriber
from models import Summary


def to_subscriber(row: dict) -> Subscriber:
    """
    Convert structured DB subscriber data into Subscriber.

    Expected DB fields:
    - id: int
    - email: str
    - name: str | None (optional)
    - active: bool (optional)
    """
    return Subscriber(
        id=row["id"],
        email=row["email"],
        name=row.get("name"),
        active=bool(row.get("active", True))
    )

def to_summary(row: dict) -> Summary:
    """
    Convert structured DB summary data into Summary.

    Expected DB fields:
    - id
    - title
    - content
    - created_at
    """
    return Summary(
        id=row["id"],
        title=row["title"],
        content=row["content"],
        created_at=row.get("created_at")
    )