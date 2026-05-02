from dataclasses import dataclass
import os

from dotenv import load_dotenv


load_dotenv()


def _parse_bool(value: str | None, default: bool = False) -> bool:
    """Convert common env-style boolean strings into a Python bool."""
    if value is None:
        return default

    return value.strip().lower() in {"1", "true", "yes", "on"}


@dataclass
class SMTPConfig:
    host: str
    port: int
    username: str
    password: str
    sender_email: str
    use_tls: bool = True


def get_smtp_config() -> SMTPConfig:
    """Load SMTP settings from environment variables.

    Raises:
        RuntimeError: If a required SMTP setting is missing or invalid.
    """
    host = os.environ.get("SMTP_HOST")
    port_raw = os.environ.get("SMTP_PORT")
    username = os.environ.get("SMTP_USERNAME")
    password = os.environ.get("SMTP_PASSWORD")
    sender_email = os.environ.get("SMTP_SENDER_EMAIL")
    use_tls = _parse_bool(os.environ.get("SMTP_USE_TLS"), default=True)

    required_values = {
        "SMTP_HOST": host,
        "SMTP_PORT": port_raw,
        "SMTP_USERNAME": username,
        "SMTP_PASSWORD": password,
        "SMTP_SENDER_EMAIL": sender_email,
    }

    missing = [key for key, value in required_values.items() if not value]
    if missing:
        raise RuntimeError(
            "Missing required SMTP environment variables: "
            + ", ".join(missing)
        )

    try:
        port = int(port_raw)
    except ValueError as exc:
        raise RuntimeError("SMTP_PORT must be a valid integer.") from exc

    return SMTPConfig(
        host=host,
        port=port,
        username=username,
        password=password,
        sender_email=sender_email,
        use_tls=use_tls,
    )
