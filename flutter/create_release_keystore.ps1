#!/usr/bin/env pwsh
# Android Release Signing Setup Script
# This script helps set up release signing for Android Play Store deployment

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Android Release Signing Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

$keystorePath = "android\app\upload-keystore.jks"
$keyPropertiesPath = "android\key.properties"

Write-Host "This script will:" -ForegroundColor Yellow
Write-Host "  1. Generate a release keystore for signing your app" -ForegroundColor White
Write-Host "  2. Create key.properties configuration file" -ForegroundColor White
Write-Host "  3. Configure build.gradle.kts for release signing" -ForegroundColor White
Write-Host ""

# Check if keystore already exists
if (Test-Path $keystorePath) {
    Write-Host "[WARNING] Keystore already exists: $keystorePath" -ForegroundColor Yellow
    $overwrite = Read-Host "Do you want to create a new keystore? (yes/no)"
    if ($overwrite -ne "yes") {
        Write-Host "Skipping keystore creation..." -ForegroundColor Yellow
        exit 0
    }
}

Write-Host ""
Write-Host "Step 1: Generate Keystore" -ForegroundColor Cyan
Write-Host ""

Write-Host "Enter the following information for your keystore:" -ForegroundColor Yellow
Write-Host "(Press Enter to use defaults shown in brackets)" -ForegroundColor Gray
Write-Host ""

$keyPassword = Read-Host "Enter key password (min 6 characters)" -AsSecureString
$keyPasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($keyPassword)
)

if ($keyPasswordPlain.Length -lt 6) {
    Write-Host "[ERROR] Password must be at least 6 characters" -ForegroundColor Red
    exit 1
}

$storePassword = Read-Host "Enter store password (min 6 characters)" -AsSecureString
$storePasswordPlain = [Runtime.InteropServices.Marshal]::PtrToStringAuto(
    [Runtime.InteropServices.Marshal]::SecureStringToBSTR($storePassword)
)

if ($storePasswordPlain.Length -lt 6) {
    Write-Host "[ERROR] Password must be at least 6 characters" -ForegroundColor Red
    exit 1
}

$keyAlias = Read-Host "Enter key alias [upload]"
if (-not $keyAlias) { $keyAlias = "upload" }

$cn = Read-Host "Enter your full name [Job Search Team]"
if (-not $cn) { $cn = "Job Search Team" }

$ou = Read-Host "Enter organizational unit [Development]"
if (-not $ou) { $ou = "Development" }

$o = Read-Host "Enter organization name [Job Search Mobile]"
if (-not $o) { $o = "Job Search Mobile" }

$l = Read-Host "Enter city/locality [San Francisco]"
if (-not $l) { $l = "San Francisco" }

$s = Read-Host "Enter state/province [California]"
if (-not $s) { $s = "California" }

$c = Read-Host "Enter country code (2 letters) [US]"
if (-not $c) { $c = "US" }

Write-Host ""
Write-Host "Generating keystore..." -ForegroundColor Yellow

# Generate keystore using keytool
$dname = "CN=$cn, OU=$ou, O=$o, L=$l, S=$s, C=$c"

try {
    $keytoolCmd = "keytool"
    
    # Create keystore
    $args = @(
        "-genkeypair",
        "-v",
        "-keystore", "`"$keystorePath`"",
        "-storetype", "JKS",
        "-keyalg", "RSA",
        "-keysize", "2048",
        "-validity", "10000",
        "-alias", $keyAlias,
        "-storepass", $storePasswordPlain,
        "-keypass", $keyPasswordPlain,
        "-dname", "`"$dname`""
    )
    
    $process = Start-Process -FilePath $keytoolCmd -ArgumentList $args -Wait -NoNewWindow -PassThru
    
    if ($process.ExitCode -eq 0) {
        Write-Host "[OK] Keystore created successfully!" -ForegroundColor Green
    } else {
        Write-Host "[ERROR] Failed to create keystore" -ForegroundColor Red
        exit 1
    }
    
} catch {
    Write-Host "[ERROR] Failed to generate keystore" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    Write-Host ""
    Write-Host "Make sure Java JDK is installed and keytool is in your PATH" -ForegroundColor Yellow
    exit 1
}

Write-Host ""
Write-Host "Step 2: Create key.properties" -ForegroundColor Cyan
Write-Host ""

# Create key.properties file
$keyPropertiesContent = @"
storePassword=$storePasswordPlain
keyPassword=$keyPasswordPlain
keyAlias=$keyAlias
storeFile=upload-keystore.jks
"@

Set-Content -Path $keyPropertiesPath -Value $keyPropertiesContent

Write-Host "[OK] Created $keyPropertiesPath" -ForegroundColor Green

Write-Host ""
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "IMPORTANT SECURITY NOTES:" -ForegroundColor Red
Write-Host "  1. Keep upload-keystore.jks file safe and backed up" -ForegroundColor Yellow
Write-Host "  2. NEVER commit key.properties or .jks file to version control" -ForegroundColor Yellow
Write-Host "  3. Store passwords in a secure password manager" -ForegroundColor Yellow
Write-Host "  4. If you lose the keystore, you cannot update your app" -ForegroundColor Yellow
Write-Host ""
Write-Host "Files created:" -ForegroundColor Cyan
Write-Host "  - $keystorePath" -ForegroundColor White
Write-Host "  - $keyPropertiesPath" -ForegroundColor White
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Build release APK: flutter build apk --release" -ForegroundColor White
Write-Host "  2. Build App Bundle: flutter build appbundle --release" -ForegroundColor White
Write-Host "  3. Test release build before uploading to Play Store" -ForegroundColor White
Write-Host ""
