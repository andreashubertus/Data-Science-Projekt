from .models import Subscriber, EmailMessage, DeliveryResult


def send_email(subscriber: Subscriber, email_message: EmailMessage) -> DeliveryResult:
    """
    Send one email to one subscriber.

    This is a placeholder implementation for testing the mailing workflow.
    Replace with real SMTP logic later.
    """
    print(f"Sending to: {subscriber.email}")
    print(f"Subject: {email_message.subject}")

    return DeliveryResult(
        subscriber_email=subscriber.email,
        success=True,
        error_message=None
    )