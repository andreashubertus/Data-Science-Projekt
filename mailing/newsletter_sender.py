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
    8. return a list with a results
    """

    summary_row = db_handler.get_latest_unsent_summary()
    summary = mappers.to_summary(summary_row)

    subscriber_rows = db_handler.get_active_subscribers()
    subscribers = [mappers.to_subscriber(row) for row in subscriber_rows]

    email_message = build_email(summary)

    results = []

    for subscriber in subscribers:
        result = send_email(subscriber, email_message)


        db_handler.save_delivery_result(
            summary_id=summary.id,
            subscriber_id=subscriber.id,
            success=result.success,
            error_message=result.error_message
        ) 

        results.append(result)

    # Mark summary as sent after processing all subscribers
    db_handler.mark_summary_as_sent(summary.id)

    return results



"""
TODO (DB layer):

We need the following DB handler functions for mailing:

1. get_latest_unsent_summary() -> dict
   Should return:
   {
       "id": int,
       "title": str,
       "content": str,
       "created_at": str | None
   }

2. get_active_subscribers() -> list[dict]
   Should return:
   [
       {
           "id": int,
           "email": str,
           "name": str | None,
           "active": bool
       }
   ]

3. save_delivery_result(
       summary_id: int,
       subscriber_id: int,
       success: bool,
       error_message: str | None
   ) -> None
   Should store the result of sending one email.

4. mark_summary_as_sent(summary_id: int) -> None
   Should mark summary as already sent to avoid duplicates.

Expected DB tables / fields for mailing:

summaries:
- id: int
- title: str
- content: str
- created_at: str | None
- sent: bool

subscribers:
- id: int
- email: str
- name: str | None
- active: bool
- subscribed_at: str | None

delivery_results:
- id: int
- summary_id: int
- subscriber_id: int
- success: bool
- error_message: str | None
- sent_at: str | None
"""