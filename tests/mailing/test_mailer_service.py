from mailing.mailer_service import send_email
from mailing.models import Subscriber, EmailMessage


def test_send_email_success():
    subscriber = Subscriber(
        id=1,
        email="user@example.com",
        name="Alice",
        active=True
    )

    email = EmailMessage(
        subject="Test",
        text_body="Hello",
        html_body="<p>Hello</p>"
    )

    result = send_email(subscriber, email)

    assert result.success is True
    assert result.subscriber_email == "user@example.com"
    assert result.error_message is None



def test_send_email_returns_failure_for_fail_address():
    subscriber = Subscriber(
        id=2,
        email="fail@example.com",  # triggers simulated failure
        name="Bob",
        active=True
    )

    email = EmailMessage(
        subject="Test",
        text_body="Hello",
        html_body="<p>Hello</p>"
    )

    result = send_email(subscriber, email)

    assert result.success is False
    assert result.subscriber_email == "fail@example.com"
    assert result.error_message is not None
