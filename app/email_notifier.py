import smtplib
from email.message import EmailMessage


def send_email_notification(
    smtp_host: str,
    smtp_port: int,
    smtp_username: str,
    smtp_password: str,
    sender: str,
    recipient: str,
    subject: str,
    body: str,
) -> None:
    msg = EmailMessage()
    msg["From"] = sender
    msg["To"] = recipient
    msg["Subject"] = subject
    msg.set_content(body)

    with smtplib.SMTP(smtp_host, smtp_port) as server:
        server.starttls()
        server.login(smtp_username, smtp_password)
        server.send_message(msg)