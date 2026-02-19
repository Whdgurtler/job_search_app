#!/usr/bin/env pwsh
# Environment Switcher Script for Windows
# Usage: .\set_environment.ps1 -Environment production

param(
    [Parameter(Mandatory=$true)]
    [ValidateSet("development", "dev", "staging", "production", "prod")]
    [string]$Environment
)

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Environment Configuration Switcher" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Normalize environment name
$envFile = switch ($Environment) {
    "development" { ".env.dev" }
    "dev" { ".env.dev" }
    "staging" { ".env.staging" }
    "production" { ".env.prod" }
    "prod" { ".env.prod" }
}

# Check if environment file exists
if (-not (Test-Path $envFile)) {
    Write-Host "[ERROR] Environment file not found: $envFile" -ForegroundColor Red
    Write-Host ""
    Write-Host "Available environment files:" -ForegroundColor Yellow
    Get-ChildItem .env.* | ForEach-Object { Write-Host "  - $($_.Name)" -ForegroundColor White }
    exit 1
}

# Backup current .env if it exists
if (Test-Path ".env") {
    $backupName = ".env.backup.$(Get-Date -Format 'yyyyMMdd_HHmmss')"
    Copy-Item ".env" $backupName
    Write-Host "[INFO] Backed up current .env to $backupName" -ForegroundColor Yellow
}

# Copy environment file
Copy-Item $envFile ".env" -Force

Write-Host "[OK] Switched to $Environment environment" -ForegroundColor Green
Write-Host ""

# Display current configuration
Write-Host "Current Configuration:" -ForegroundColor Cyan
Get-Content ".env" | ForEach-Object {
    if ($_ -match "^([^=]+)=(.+)$") {
        $key = $matches[1]
        $value = $matches[2]
        Write-Host "  $key = $value" -ForegroundColor White
    }
}

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Run: flutter pub get" -ForegroundColor White
Write-Host "  2. Restart your app or rebuild" -ForegroundColor White

if ($Environment -eq "production" -or $Environment -eq "prod") {
    Write-Host ""
    Write-Host "⚠️  PRODUCTION ENVIRONMENT ACTIVE" -ForegroundColor Red
    Write-Host "Build release:" -ForegroundColor Yellow
    Write-Host "  flutter build appbundle --release" -ForegroundColor White
}

Write-Host ""
