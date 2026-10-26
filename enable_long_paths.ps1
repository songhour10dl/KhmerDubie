# Enable Windows Long Path Support for KhmerDub Studio
# This script must be run as Administrator

Write-Host "Checking if running as Administrator..." -ForegroundColor Yellow

$isAdmin = ([Security.Principal.WindowsPrincipal] [Security.Principal.WindowsIdentity]::GetCurrent()).IsInRole([Security.Principal.WindowsBuiltInRole]::Administrator)

if (-not $isAdmin) {
    Write-Host "ERROR: This script must be run as Administrator!" -ForegroundColor Red
    Write-Host ""
    Write-Host "Right-click on PowerShell and select 'Run as Administrator', then run this script again." -ForegroundColor Yellow
    Write-Host ""
    Read-Host "Press Enter to exit"
    exit 1
}

Write-Host "Running as Administrator - proceeding with Long Path enablement..." -ForegroundColor Green
Write-Host ""

# Enable Long Paths in Registry
try {
    Write-Host "Enabling Long Path support in Windows Registry..." -ForegroundColor Cyan
    
    $regPath = "HKLM:\SYSTEM\CurrentControlSet\Control\FileSystem"
    $regName = "LongPathsEnabled"
    $regValue = 1
    
    # Check current value
    $currentValue = (Get-ItemProperty -Path $regPath -Name $regName -ErrorAction SilentlyContinue).$regName
    
    if ($currentValue -eq 1) {
        Write-Host "✓ Long Path support is already enabled!" -ForegroundColor Green
    } else {
        Set-ItemProperty -Path $regPath -Name $regName -Value $regValue -Type DWord
        Write-Host "✓ Long Path support has been enabled successfully!" -ForegroundColor Green
    }
    
    Write-Host ""
    Write-Host "IMPORTANT: You may need to restart your computer for changes to take effect." -ForegroundColor Yellow
    Write-Host ""
    Write-Host "After restart, run: pip install -r requirements.txt" -ForegroundColor Cyan
    Write-Host ""
    
} catch {
    Write-Host "ERROR: Failed to enable Long Path support: $_" -ForegroundColor Red
    exit 1
}

Write-Host "Press Enter to exit..."
Read-Host
