from .models import DeliveryResult
from . import mappers
from .content_builder import build_email
from .mailer_service import send_email

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
        return []

    summary = mappers.to_summary(summary_row)

    subscriber_rows = db_handler.get_active_subscribers(summary.category) or []
    subscribers = [mappers.to_subscriber(row) for row in subscriber_rows]

    if not subscribers:
        return []

    email_message = build_email(summary)

    results = []

    for subscriber in subscribers:
        if subscriber.category != summary.category:
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

    return results
