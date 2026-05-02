from app.email_notifier import send_email_notification


def send_degraded_notification(
    smtp_host: str,
    smtp_port: int,
    smtp_username: str,
    smtp_password: str,
    sender: str,
    recipient: str,
    subject: str,
    body: str,
) -> None:
    send_email_notification(
        smtp_host=smtp_host,
        smtp_port=smtp_port,
        smtp_username=smtp_username,
        smtp_password=smtp_password,
        sender=sender,
        recipient=recipient,
        subject=subject,
        body=body,
    )