# GitHub Secrets Setup

Configure these repository secrets:

## Required
- `OPENAI_API_KEY`
- `OPENAI_MODEL`
- `GOOGLE_DRIVE_TARGET_FOLDER_ID`
- `GOOGLE_SERVICE_ACCOUNT_JSON`

## Email notification
- `EMAIL_NOTIFY_TO`
- `EMAIL_NOTIFY_ENABLED`
- `SMTP_HOST`
- `SMTP_PORT`
- `SMTP_USERNAME`
- `SMTP_PASSWORD`
- `SMTP_SENDER`

## Recommended values
- `OPENAI_MODEL` = `gpt-5`
- `GOOGLE_DRIVE_TARGET_FOLDER_ID` = `1KdRuyLOb4z89Vsi_M6MLYbOIJUivhfiF`
- `EMAIL_NOTIFY_ENABLED` = `true`

## Important
`GOOGLE_SERVICE_ACCOUNT_JSON` must contain the full one-line JSON credential for the service account. The service account email must have edit access to the target Google Drive folder.

## Drive permission requirement
Share the target folder with the service account email as **Editor**.