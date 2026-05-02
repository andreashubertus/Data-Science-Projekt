from .models import Subscriber
from .models import Summary


class MailingDataError(ValueError):
    """Raised when DB data for the mailing flow is missing or invalid."""


def to_subscriber(row: dict) -> Subscriber:
    """
    Convert structured DB subscriber data into Subscriber.

    Expected DB fields:
    - id: int
    - email: str
    - name: str | None (optional)
    - active: bool (optional)
    """
    if row is None:
        raise MailingDataError("Subscriber row is missing.")

    subscriber_id = row.get("id")
    if subscriber_id is None:
        raise MailingDataError("Subscriber row is missing required field 'id'.")

    email = row.get("email")
    if not email:
        raise MailingDataError("Subscriber row is missing required field 'email'.")

    return Subscriber(
        id=subscriber_id,
        email=email,
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
    if row is None:
        raise MailingDataError("Summary row is missing.")

    summary_id = row.get("id")
    if summary_id is None:
        raise MailingDataError("Summary row is missing required field 'id'.")

    title = row.get("title")
    if not title:
        raise MailingDataError("Summary row is missing required field 'title'.")

    content = row.get("content")
    if not content:
        raise MailingDataError("Summary row is missing required field 'content'.")

    return Summary(
        id=summary_id,
        title=title,
        content=content,
        created_at=row.get("created_at")
    )
