from email.message import EmailMessage as SMTPEmailMessage
import logging
import smtplib

from .models import Subscriber, EmailMessage, DeliveryResult
from .config_mailing import get_smtp_config

logger = logging.getLogger(__name__)

def send_email(subscriber: Subscriber, email_message: EmailMessage) -> DeliveryResult:
    """
    Send one email to one subscriber.

    Builds a real stdlib email message and sends it over SMTP.
    """
    smtp_config = get_smtp_config()

    try:
        logger.info(f"Sending email to {subscriber.email}")
        logger.debug(f"Subject: {email_message.subject}")

        message = SMTPEmailMessage()
        message["From"] = smtp_config.sender_email
        message["To"] = subscriber.email
        message["Subject"] = email_message.subject
        message.set_content(email_message.text_body)

        if email_message.html_body:
            message.add_alternative(email_message.html_body, subtype="html")

        with smtplib.SMTP(smtp_config.host, smtp_config.port) as server:
            if smtp_config.use_tls:
                server.starttls()

            server.login(smtp_config.username, smtp_config.password)
            server.send_message(message)

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
