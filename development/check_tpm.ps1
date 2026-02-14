# TPM Status Check Script
Write-Host "=== TPM Status Check ===" -ForegroundColor Cyan

try {
    $tpm = Get-Tpm
    Write-Host "`nTPM Information:" -ForegroundColor Green
    Write-Host "  TpmPresent    : $($tpm.TpmPresent)"
    Write-Host "  TpmReady      : $($tpm.TpmReady)"
    Write-Host "  TpmEnabled    : $($tpm.TpmEnabled)"
    Write-Host "  TpmActivated  : $($tpm.TpmActivated)"
    Write-Host "  TpmOwned      : $($tpm.TpmOwned)"
    Write-Host "  Manufacturer  : $($tpm.ManufacturerIdTxt)"
    Write-Host "  Spec Version  : $($tpm.ManufacturerVersion)"
} catch {
    Write-Host "`nError: $($_.Exception.Message)" -ForegroundColor Red
    Write-Host "`nPossible reasons:" -ForegroundColor Yellow
    Write-Host "  1. Administrative privileges required"
    Write-Host "  2. TPM is not present on this system"
    Write-Host "  3. TPM is disabled in BIOS/UEFI"
}

Write-Host "`n=== Alternative Check: Security Devices ===" -ForegroundColor Cyan
Get-PnpDevice -Class SecurityDevices -ErrorAction SilentlyContinue |
    Where-Object {$_.FriendlyName -like '*TPM*' -or $_.FriendlyName -like '*Trusted*'} |
    Select-Object FriendlyName, Status

Write-Host "`n=== Registry Check ===" -ForegroundColor Cyan
if (Test-Path 'HKLM:\SYSTEM\CurrentControlSet\Services\TPM') {
    Write-Host "TPM service registry entry: EXISTS"
} else {
    Write-Host "TPM service registry entry: NOT FOUND"
}
