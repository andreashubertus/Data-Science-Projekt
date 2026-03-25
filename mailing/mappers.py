from models import Subscriber


def email_to_subscriber(email: str, idx: int) -> Subscriber:
    return Subscriber(
        id=idx,          # temporary fallback: DB should provide real subscriber ID
        email=email,
        name=None,       # temporary fallback: DB may include name later
        active=True      # temporary fallback: DB should provide active/unsubscribed flag
)