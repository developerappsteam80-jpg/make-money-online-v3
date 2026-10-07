
import os, hashlib, secrets, smtplib
from pathlib import Path
from email.message import EmailMessage

ROOT = Path(__file__).resolve().parent.parent
DATA = Path(os.getenv("DATA_DIR", str(ROOT / "data")))
PDF = DATA / "uploads" / "ebook.pdf"

def token():
    return secrets.token_urlsafe(32)

def token_hash(value):
    return hashlib.sha256(value.encode()).hexdigest()

def send_email(to, url, order_id):
    host = os.getenv("SMTP_HOST", "")
    sender = os.getenv("SMTP_FROM", "") or os.getenv("SMTP_USERNAME", "")
    if not host or not sender:
        return False

    msg = EmailMessage()
    msg["Subject"] = "Your Make Money Online ebook is ready"
    msg["From"] = sender
    msg["To"] = to
    msg.set_content(
        f"Thank you for your purchase!\n\n"
        f"Your secure ebook download:\n{url}\n\n"
        f"Order: {order_id}"
    )

    with smtplib.SMTP(host, int(os.getenv("SMTP_PORT", "587"))) as server:
        server.starttls()
        if os.getenv("SMTP_USERNAME"):
            server.login(
                os.getenv("SMTP_USERNAME", ""),
                os.getenv("SMTP_PASSWORD", "")
            )
        server.send_message(msg)
    return True
