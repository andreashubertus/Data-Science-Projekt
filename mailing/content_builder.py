from .models import Summary, EmailMessage
from datetime import datetime

def build_email(summary: Summary) -> EmailMessage:
    date_str = ""

    if summary.created_at:
        date = datetime.fromisoformat(summary.created_at)
        date_str = date.strftime("%d.%m")

    if date_str:
        subject = f"AI News Summary ({date_str}): {summary.title}"
    else:
        subject = f"AI News Summary: {summary.title}"

    text_body = f"{summary.title}\n\n{summary.content}"

    html_body = f"""
    <html>
        <body>
            <h1>{summary.title}</h1>
            <p>{summary.content}</p>
        </body>
    </html>
    """

    return EmailMessage(
        subject=subject,
        text_body=text_body,
        html_body=html_body
    )