import logging

from .models import DeliveryResult
from . import mappers
from .content_builder import build_email
from .mailer_service import send_email


logger = logging.getLogger(__name__)


def send_latest_newsletter(db_handler) -> list[DeliveryResult]:
    """
    1. get summary from DB
    2. get subscribers from DB
    3. convert DB data → dataclasses (mappers)
    4. build email content
    5. send to each subscriber
    6. collect results
    7. save results in DB (call db_handler.save_delivery_result(...))
    8. return a list of delivery results
    """

    summary_row = db_handler.get_latest_unsent_summary()
    if summary_row is None:
        logger.info("No unsent summary found. Skipping newsletter delivery.")
        return []

    summary = mappers.to_summary(summary_row)
    logger.info(
        "Starting newsletter delivery for summary_id=%s, category=%s.",
        summary.id,
        summary.category,
    )

    subscriber_rows = db_handler.get_active_subscribers(summary.category) or []
    subscribers = [mappers.to_subscriber(row) for row in subscriber_rows]
    logger.info(
        "Loaded %s active subscriber(s) for category=%s.",
        len(subscribers),
        summary.category,
    )

    if not subscribers:
        logger.info(
            "No subscribers found for category=%s. Skipping delivery.",
            summary.category,
        )
        return []

    email_message = build_email(summary)
    logger.info(
        "Built email content for summary_id=%s with subject=%r.",
        summary.id,
        email_message.subject,
    )

    results = []

    for subscriber in subscribers:
        if subscriber.category != summary.category:
            logger.error(
                "Subscriber category mismatch for subscriber_id=%s: %r != %r.",
                subscriber.id,
                subscriber.category,
                summary.category,
            )
            raise mappers.MailingDataError(
                f"Subscriber category {subscriber.category!r} does not match summary category {summary.category!r}."
            )

        result = send_email(subscriber, email_message)

        db_handler.save_delivery_result(
            summary_id=summary.id,
            subscriber_id=subscriber.id,
            success=result.success,
            error_message=result.error_message
        ) 

        results.append(result)

    db_handler.mark_summary_as_sent(summary.id)
    logger.info(
        "Finished newsletter delivery for summary_id=%s. Marked summary as sent.",
        summary.id,
    )

    return results
