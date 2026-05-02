from .models import Summary, EmailMessage
from datetime import datetime
from .mappers import MailingDataError

def build_email(summary: Summary) -> EmailMessage:
    if not summary.category:
        raise MailingDataError("Cannot build email without a summary category.")

    if not summary.title:
        raise MailingDataError("Cannot build email without a summary title.")

    if not summary.content:
        raise MailingDataError("Cannot build email without summary content.")

    date_str = ""

    if summary.created_at:
        date = datetime.fromisoformat(summary.created_at)
        date_str = date.strftime("%d.%m")

    if date_str:
        subject = f"AI News Summary [{summary.category}] ({date_str}): {summary.title}"
    else:
        subject = f"AI News Summary [{summary.category}]: {summary.title}"

    text_body = (
        f"AI News Summary\n"
        f"Category: {summary.category}\n"
        f"Title: {summary.title}\n"
        f"{'Date: ' + date_str if date_str else ''}\n\n"
        f"{summary.content}\n"
    )

    html_body = f"""
    <html>
        <body style="margin:0; padding:0; background-color:#f3f4f6; font-family:Arial, Helvetica, sans-serif; color:#1f2937;">
            <div style="max-width:680px; margin:0 auto; padding:32px 20px;">
                <div style="background-color:#ffffff; border:1px solid #e5e7eb; border-radius:16px; overflow:hidden;">
                    <div style="background:linear-gradient(135deg, #0f172a, #1d4ed8); padding:24px 28px; color:#ffffff;">
                        <p style="margin:0 0 10px 0; font-size:12px; letter-spacing:1.2px; text-transform:uppercase; opacity:0.85;">
                            AI News Summary
                        </p>
                        <h1 style="margin:0; font-size:30px; line-height:1.2;">
                            {summary.title}
                        </h1>
                    </div>
                    <div style="padding:24px 28px 28px 28px;">
                        <div style="margin-bottom:20px;">
                            <span style="display:inline-block; background-color:#dbeafe; color:#1d4ed8; border-radius:999px; padding:6px 12px; font-size:12px; font-weight:bold; letter-spacing:0.4px; text-transform:uppercase;">
                                {summary.category}
                            </span>
                            {f'<span style="margin-left:12px; color:#6b7280; font-size:14px;">{date_str}</span>' if date_str else ''}
                        </div>
                        <p style="margin:0; font-size:16px; line-height:1.7; color:#374151; white-space:pre-line;">
                            {summary.content}
                        </p>
                    </div>
                </div>
            </div>
        </body>
    </html>
    """

    return EmailMessage(
        subject=subject,
        text_body=text_body,
        html_body=html_body
    )
