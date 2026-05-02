# Philippines Mission Intel Report Runbook

## Daily schedule
- Source cutoff target: 2350Z
- Publication target: 0001Z
- Retry windows: +10 min and +25 min equivalent in process logic

## Expected outputs
Top-level folder:
- `LATEST - Philippines Mission Intel Status Report.docx`
- `LATEST - Philippines Mission Intel Status Report.pdf`

Archive subfolder:
- `Philippines_Mission_Intel_Status_Report_YYYY-MM-DD_0001Z.docx`
- `Philippines_Mission_Intel_Status_Report_YYYY-MM-DD_0001Z.pdf`

Source_Logs subfolder:
- `Philippines_Mission_Intel_Status_Report_YYYY-MM-DD_0001Z.source_log.json`
- `Philippines_Mission_Intel_Status_Report_YYYY-MM-DD_0001Z.validation.json`
- `Philippines_Mission_Intel_Status_Report_YYYY-MM-DD_0001Z.manifest.json`

## First-run checks
1. Run workflow manually with `workflow_dispatch`
2. Confirm no validation failure
3. Confirm subfolders created:
   - `Archive`
   - `Source_Logs`
   - `Failures`
4. Confirm `LATEST` file exists
5. Confirm archive file exists
6. Confirm source log and validation file exist
7. Confirm email notification received if enabled

## Failure drill
If run status is failed:
1. Check GitHub Actions logs
2. Inspect uploaded artifact bundle
3. Review `validation.json`
4. Review source fetch failures
5. Confirm Drive credentials and permissions
6. Re-run manually after correction

## Degraded drill
If run status is degraded:
1. Review stale exclusions
2. Review source failures
3. Check whether official sources were unavailable
4. Determine whether degraded output is still mission-usable

## Hard rules
- Failed output does not replace `LATEST`
- UTC is authoritative
- Official sources outrank secondary reporting