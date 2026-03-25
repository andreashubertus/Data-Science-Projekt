from dataclasses import dataclass


@dataclass
class Subscriber:
    id: int
    email: str
    name: str | None = None
    active: bool = True


@dataclass
class Summary:
    id: int
    title: str
    content: str
    created_at: str | None = None


@dataclass
class EmailMessage:
    subject: str
    text_body: str
    html_body: str | None = None


@dataclass
class DeliveryResult:
    subscriber_email: str
    success: bool
    error_message: str | None = None