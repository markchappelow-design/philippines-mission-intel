import os
from dataclasses import dataclass
from dotenv import load_dotenv

load_dotenv()


@dataclass(frozen=True)
class Settings:
    openai_api_key: str
    openai_model: str
    google_drive_target_folder_id: str
    google_service_account_json: str
    report_title: str
    report_publish_time_utc: str
    source_cutoff_time_utc: str
    email_notify_to: str
    email_notify_enabled: bool
    smtp_host: str
    smtp_port: int
    smtp_username: str
    smtp_password: str
    smtp_sender: str
    sms_notify_enabled: bool
    pdf_output_enabled: bool


def _to_bool(value: str, default: bool = False) -> bool:
    if value is None:
        return default
    return value.strip().lower() in {"1", "true", "yes", "on"}


def get_settings() -> Settings:
    return Settings(
        openai_api_key=os.getenv("OPENAI_API_KEY", "").strip(),
        openai_model=os.getenv("OPENAI_MODEL", "gpt-5").strip(),
        google_drive_target_folder_id=os.getenv("GOOGLE_DRIVE_TARGET_FOLDER_ID", "").strip(),
        google_service_account_json=os.getenv("GOOGLE_SERVICE_ACCOUNT_JSON", "").strip(),
        report_title=os.getenv("REPORT_TITLE", "Philippines Mission Intel Status Report").strip(),
        report_publish_time_utc=os.getenv("REPORT_PUBLISH_TIME_UTC", "0001").strip(),
        source_cutoff_time_utc=os.getenv("SOURCE_CUTOFF_TIME_UTC", "2350").strip(),
        email_notify_to=os.getenv("EMAIL_NOTIFY_TO", "").strip(),
        email_notify_enabled=_to_bool(os.getenv("EMAIL_NOTIFY_ENABLED", "false")),
        smtp_host=os.getenv("SMTP_HOST", "").strip(),
        smtp_port=int(os.getenv("SMTP_PORT", "587").strip()),
        smtp_username=os.getenv("SMTP_USERNAME", "").strip(),
        smtp_password=os.getenv("SMTP_PASSWORD", "").strip(),
        smtp_sender=os.getenv("SMTP_SENDER", "").strip(),
        sms_notify_enabled=_to_bool(os.getenv("SMS_NOTIFY_ENABLED", "false")),
        pdf_output_enabled=_to_bool(os.getenv("PDF_OUTPUT_ENABLED", "true")),
    )


def validate_settings(settings: Settings) -> None:
    required = {
        "OPENAI_API_KEY": settings.openai_api_key,
        "GOOGLE_DRIVE_TARGET_FOLDER_ID": settings.google_drive_target_folder_id,
        "GOOGLE_SERVICE_ACCOUNT_JSON": settings.google_service_account_json,
    }
    missing = [k for k, v in required.items() if not v]
    if missing:
        raise ValueError(f"Missing required settings: {', '.join(missing)}")