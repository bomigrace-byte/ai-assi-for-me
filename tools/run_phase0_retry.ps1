param(
    [Parameter(Mandatory = $true)]
    [long]$ResetUnix,
    [Parameter(Mandatory = $true)]
    [string]$OutputPath
)

$ErrorActionPreference = 'Stop'
$remaining = $ResetUnix - [DateTimeOffset]::UtcNow.ToUnixTimeSeconds()
if ($remaining -gt 0) {
    Start-Sleep -Seconds $remaining
}

$scriptPath = Join-Path $PSScriptRoot 'validate_star_history.ps1'
try {
    & $scriptPath -PauseMilliseconds 500 | Set-Content -LiteralPath $OutputPath -Encoding UTF8
    Add-Content -LiteralPath $OutputPath -Value "`nRETRY_STATUS=COMPLETED" -Encoding UTF8
}
catch {
    "RETRY_STATUS=ERROR`n$($_.Exception.Message)" | Set-Content -LiteralPath $OutputPath -Encoding UTF8
}
