from models import DeliveryResult

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
    pass