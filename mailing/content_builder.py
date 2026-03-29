from .models import Summary, EmailMessage


def build_email(summary: Summary) -> EmailMessage:
    subject = summary.title
    text_body = summary.content


    html_body = "html body" # to do: build html

    return EmailMessage(
        subject=subject,
        text_body=text_body,
        html_body=html_body
)