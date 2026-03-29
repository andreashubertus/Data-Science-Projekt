from models import DeliveryResult
import mappers
from content_builder import build_email
from mailer_service import send_email

# Mock function (TODO: replace with an actual db.function)
def get_latest_unsent_summary():
    return {
        "id": 1,
        "title": "AI Breakthrough in 2026",
        "content": "Researchers developed a new model that significantly improves reasoning tasks.",
        "created_at": "2026-03-29"
    }

# Mock function (TODO: replace with an actual db function)
def get_active_subscribers():
    """
    Temporary mock function for testing.
    Returns a list of subscribers in the expected DB format.
    """
    return [
        {
            "id": 1,
            "email": "user1@example.com",
            "name": "Alice",
            "active": True
        },
        {
            "id": 2,
            "email": "user2@example.com",
            "name": "Bob",
            "active": True
        }
    ]


def send_latest_newsletter(db_handler) -> list[DeliveryResult]:
    """
    1. get summary from DB
    2. get subscribers from DB
    3. convert DB data → dataclasses (mappers)
    4. build email content
    5. send to each subscriber
    6. collect results
    7. save results in DB (call db_handler.save_delivery_result(...))
    """

    summary_row = get_latest_unsent_summary()
    summary = mappers.to_summary(summary_row)

    subscriber_rows = get_active_subscribers()

    subscribers = [mappers.to_subscriber(row) for row in subscriber_rows]

    email_message = build_email(summary)

    for subscriber in subscribers:
        result = send_email(subscriber, email_message)
        #db_handler.save_delivery_result(results)



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