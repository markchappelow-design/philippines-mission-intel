$projectRoot = "C:\philippines-mission-intel"
$pythonExe   = "C:\Users\mchap\AppData\Local\Programs\Python\Python312\python.exe"

$logDir = Join-Path $projectRoot "logs"
New-Item -ItemType Directory -Force -Path $logDir | Out-Null
$logFile = Join-Path $logDir ("daily_report_" + (Get-Date -Format "yyyyMMdd_HHmmss") + ".log")

Set-Location $projectRoot

"Starting report run at $(Get-Date -Format o)" | Out-File -FilePath $logFile -Encoding utf8

& $pythonExe "$projectRoot\generate_report.py" *>> $logFile
$exitCode = $LASTEXITCODE

"Finished report run at $(Get-Date -Format o)" | Out-File -FilePath $logFile -Append -Encoding utf8
"Exit code: $exitCode" | Out-File -FilePath $logFile -Append -Encoding utf8

if ($exitCode -eq 0) {
    "SUCCESS $(Get-Date -Format o)" | Out-File -FilePath (Join-Path $logDir "LAST_SUCCESS.txt") -Encoding utf8
} else {
    "FAILED $(Get-Date -Format o)" | Out-File -FilePath (Join-Path $logDir "LAST_FAILURE.txt") -Encoding utf8
}

Get-ChildItem $logDir -File -Filter "*.log" |
    Where-Object { $_.LastWriteTime -lt (Get-Date).AddDays(-30) } |
    Remove-Item -Force

exit $exitCode
