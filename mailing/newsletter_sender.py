from models import Subscriber, EmailMessage, DeliveryResult


def send_email(subscriber: Subscriber, email_message: EmailMessage) -> DeliveryResult:
    print(f"Sending to: {subscriber.email}")
    print(f"Subject: {email_message.subject}")

    return DeliveryResult(
        subscriber_email=subscriber.email,
        success=True,
        error_message=None
    )