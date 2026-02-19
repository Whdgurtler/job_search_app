#!/usr/bin/env pwsh
# Firebase Configuration Update Script
# This script extracts values from google-services.json and updates firebase_options.dart

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Firebase Configuration Update Tool" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

# Check if google-services.json exists
if (-not (Test-Path "android\app\google-services.json")) {
    Write-Host "[ERROR] google-services.json not found!" -ForegroundColor Red
    Write-Host "Expected location: android\app\google-services.json" -ForegroundColor Yellow
    Write-Host ""
    Write-Host "Please download it from Firebase Console and try again." -ForegroundColor Yellow
    Write-Host "See FIREBASE_MANUAL_SETUP.md for instructions." -ForegroundColor Cyan
    exit 1
}

Write-Host "[OK] Found google-services.json" -ForegroundColor Green
Write-Host ""

# Parse the JSON file
try {
    $jsonContent = Get-Content "android\app\google-services.json" -Raw | ConvertFrom-Json
    
    $projectNumber = $jsonContent.project_info.project_number
    $projectId = $jsonContent.project_info.project_id
    $storageBucket = $jsonContent.project_info.storage_bucket
    
    # Get the first client (Android app)
    $client = $jsonContent.client[0]
    $appId = $client.client_info.mobilesdk_app_id
    $apiKey = $client.api_key[0].current_key
    
    Write-Host "Extracted Firebase Configuration:" -ForegroundColor Cyan
    Write-Host "  Project ID:       $projectId" -ForegroundColor White
    Write-Host "  Project Number:   $projectNumber" -ForegroundColor White
    Write-Host "  Storage Bucket:   $storageBucket" -ForegroundColor White
    Write-Host "  API Key:          $apiKey" -ForegroundColor White
    Write-Host "  App ID:           $appId" -ForegroundColor White
    Write-Host ""
    
} catch {
    Write-Host "[ERROR] Failed to parse google-services.json" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Update firebase_options.dart
Write-Host "Updating lib\firebase_options.dart..." -ForegroundColor Yellow

try {
    $firebaseOptionsPath = "lib\firebase_options.dart"
    
    if (-not (Test-Path $firebaseOptionsPath)) {
        Write-Host "[ERROR] firebase_options.dart not found!" -ForegroundColor Red
        exit 1
    }
    
    $content = Get-Content $firebaseOptionsPath -Raw
    
    # Replace Android configuration values
    $content = $content -replace "apiKey: 'YOUR_ANDROID_API_KEY'", "apiKey: '$apiKey'"
    $content = $content -replace "appId: '1:YOUR_APP_ID:android:YOUR_ANDROID_APP_ID'", "appId: '$appId'"
    $content = $content -replace "messagingSenderId: 'YOUR_SENDER_ID'", "messagingSenderId: '$projectNumber'"
    $content = $content -replace "projectId: 'YOUR_PROJECT_ID'", "projectId: '$projectId'"
    $content = $content -replace "storageBucket: 'YOUR_PROJECT_ID\.appspot\.com'", "storageBucket: '$storageBucket'"
    
    Set-Content $firebaseOptionsPath $content -NoNewline
    
    Write-Host "[OK] Successfully updated firebase_options.dart!" -ForegroundColor Green
    Write-Host ""
    
} catch {
    Write-Host "[ERROR] Failed to update firebase_options.dart" -ForegroundColor Red
    Write-Host $_.Exception.Message -ForegroundColor Red
    exit 1
}

# Summary
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "Configuration Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Run: flutter pub get" -ForegroundColor White
Write-Host "  2. Run: flutter run" -ForegroundColor White
Write-Host ""
Write-Host "Your Firebase project is ready!" -ForegroundColor Green
