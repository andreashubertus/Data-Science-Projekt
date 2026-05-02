import smtplib
from unittest.mock import MagicMock, patch

from src.mailing.mailer_service import send_email
from src.mailing.models import Subscriber, EmailMessage


def test_send_email_success():
    subscriber = Subscriber(
        id=1,
        email="user@example.com",
        category="TECHNOLOGY",
        name="Alice",
        active=True
    )

    email = EmailMessage(
        subject="Test",
        text_body="Hello",
        html_body="<p>Hello</p>"
    )

    smtp_config = MagicMock()
    smtp_config.host = "smtp.gmail.com"
    smtp_config.port = 587
    smtp_config.username = "sender@example.com"
    smtp_config.password = "secret"
    smtp_config.sender_email = "sender@example.com"
    smtp_config.use_tls = True

    with (
        patch("src.mailing.mailer_service.get_smtp_config", return_value=smtp_config),
        patch("src.mailing.mailer_service.smtplib.SMTP") as mock_smtp,
    ):
        result = send_email(subscriber, email)

    server = mock_smtp.return_value.__enter__.return_value

    assert result.success is True
    assert result.subscriber_email == "user@example.com"
    assert result.error_message is None
    mock_smtp.assert_called_once_with("smtp.gmail.com", 587)
    server.starttls.assert_called_once()
    server.login.assert_called_once_with("sender@example.com", "secret")
    server.send_message.assert_called_once()

def test_send_email_returns_failure_when_smtp_raises():
    subscriber = Subscriber(
        id=2,
        email="user2@example.com",
        category="SPORTS",
        name="Bob",
        active=True
    )

    email = EmailMessage(
        subject="Test",
        text_body="Hello",
        html_body="<p>Hello</p>"
    )

    smtp_config = MagicMock()
    smtp_config.host = "smtp.gmail.com"
    smtp_config.port = 587
    smtp_config.username = "sender@example.com"
    smtp_config.password = "secret"
    smtp_config.sender_email = "sender@example.com"
    smtp_config.use_tls = True

    with (
        patch("src.mailing.mailer_service.get_smtp_config", return_value=smtp_config),
        patch("src.mailing.mailer_service.smtplib.SMTP") as mock_smtp,
    ):
        server = mock_smtp.return_value.__enter__.return_value
        server.send_message.side_effect = smtplib.SMTPException("SMTP send failed")

        result = send_email(subscriber, email)

    assert result.success is False
    assert result.subscriber_email == "user2@example.com"
    assert result.error_message is not None
