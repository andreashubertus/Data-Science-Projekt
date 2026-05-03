import logging

from .models import Subscriber, EmailMessage, DeliveryResult

logger = logging.getLogger(__name__)

def send_email(subscriber: Subscriber, email_message: EmailMessage) -> DeliveryResult:
    """
    Send one email to one subscriber.

    Current behavior:
    - placeholder implementation (no real SMTP yet)
    - logs sending attempt
    - simulates failure for testing
    """

    try:
        logger.info(f"Sending email to {subscriber.email}")
        logger.debug(f"Subject: {email_message.subject}")

        # Simulate failure for testing
        if "fail" in subscriber.email:
            raise Exception("Simulated sending error")

        # Simulate successful send
        return DeliveryResult(
            subscriber_email=subscriber.email,
            success=True,
            error_message=None
        )
    except Exception as e:
        logger.error(f"Failed to send email to {subscriber.email}: {e}")

        return DeliveryResult(
            subscriber_email=subscriber.email,
            success=False,
            error_message=str(e)
        )