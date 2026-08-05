# 1. Ensure the Windows Update module is installed
if (-not (Get-Module -ListAvailable -Name PSWindowsUpdate)) {
    Write-Host "Installing PSWindowsUpdate module..." -ForegroundColor Cyan
    Install-Module -Name PSWindowsUpdate -Force -SkipPublisherCheck -AllowClobber
}

# 2. Import the module into the current session
Import-Module PSWindowsUpdate

# 3. Scan and install driver updates automatically
Write-Host "Scanning and installing missing drivers..." -ForegroundColor Cyan
Get-WindowsUpdate -Category "Drivers" -Install -AcceptAll -AutoReboot
