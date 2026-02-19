#!/usr/bin/env pwsh
# iOS Firebase Configuration Setup Script

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "iOS Firebase Configuration Setup" -ForegroundColor Cyan
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""

Write-Host "Follow these steps to configure iOS Firebase:" -ForegroundColor Yellow
Write-Host ""

Write-Host "Step 1: Open Firebase Console" -ForegroundColor Cyan
Write-Host "  1. Go to: https://console.firebase.google.com/project/job-search-mobile" -ForegroundColor White
Write-Host ""

$projectUrl = "https://console.firebase.google.com/project/job-search-mobile/settings/general"
Write-Host "Opening Project Settings..." -ForegroundColor Yellow
Start-Process $projectUrl

Write-Host ""
Read-Host "Press Enter after the page opens"

Write-Host ""
Write-Host "Step 2: Add iOS App" -ForegroundColor Cyan
Write-Host "In the browser (Project Settings):" -ForegroundColor White
Write-Host "  1. Scroll down to 'Your apps' section" -ForegroundColor White
Write-Host "  2. Click the Apple icon (iOS)" -ForegroundColor White
Write-Host "  3. iOS bundle ID: com.jobsearch.mobile" -ForegroundColor Green
Write-Host "  4. App nickname: Job Search Mobile iOS" -ForegroundColor White
Write-Host "  5. Click 'Register app'" -ForegroundColor White
Write-Host "  6. Download 'GoogleService-Info.plist'" -ForegroundColor Yellow
Write-Host "  7. Save it to: ios\Runner\GoogleService-Info.plist" -ForegroundColor Yellow
Write-Host "  8. Click through the remaining steps" -ForegroundColor White
Write-Host ""

Read-Host "Press Enter after downloading GoogleService-Info.plist"

Write-Host ""
Write-Host "Step 3: Verify and Update Configuration" -ForegroundColor Cyan

if (Test-Path "ios\Runner\GoogleService-Info.plist") {
    Write-Host "[OK] Found GoogleService-Info.plist" -ForegroundColor Green
    Write-Host ""
    
    try {
        # Parse the plist file
        [xml]$plistContent = Get-Content "ios\Runner\GoogleService-Info.plist"
        
        $dict = $plistContent.plist.dict
        $keys = $dict.key
        $values = $dict.string
        
        # Extract values
        $apiKey = ""
        $bundleId = ""
        $clientId = ""
        $reversedClientId = ""
        $projectId = ""
        $storageBucket = ""
        $gcmSenderId = ""
        $appId = ""
        
        for ($i = 0; $i -lt $keys.Count; $i++) {
            switch ($keys[$i]) {
                "API_KEY" { $apiKey = $values[$i] }
                "BUNDLE_ID" { $bundleId = $values[$i] }
                "CLIENT_ID" { $clientId = $values[$i] }
                "REVERSED_CLIENT_ID" { $reversedClientId = $values[$i] }
                "GCM_SENDER_ID" { $gcmSenderId = $values[$i] }
                "GOOGLE_APP_ID" { $appId = $values[$i] }
                "PROJECT_ID" { $projectId = $values[$i] }
                "STORAGE_BUCKET" { $storageBucket = $values[$i] }
            }
        }
        
        Write-Host "Extracted iOS Firebase Configuration:" -ForegroundColor Cyan
        Write-Host "  Project ID:      $projectId" -ForegroundColor White
        Write-Host "  Bundle ID:       $bundleId" -ForegroundColor White
        Write-Host "  API Key:         $apiKey" -ForegroundColor White
        Write-Host "  App ID:          $appId" -ForegroundColor White
        Write-Host "  GCM Sender ID:   $gcmSenderId" -ForegroundColor White
        Write-Host ""
        
        # Update firebase_options.dart
        Write-Host "Updating lib\firebase_options.dart..." -ForegroundColor Yellow
        
        $firebaseOptionsPath = "lib\firebase_options.dart"
        $content = Get-Content $firebaseOptionsPath -Raw
        
        # Replace iOS configuration values
        $content = $content -replace "apiKey: 'YOUR_IOS_API_KEY'", "apiKey: '$apiKey'"
        $content = $content -replace "appId: '1:YOUR_APP_ID:ios:YOUR_IOS_APP_ID'", "appId: '$appId'"
        $content = $content -replace "iosBundleId: 'com\.jobsearch\.mobile'", "iosBundleId: '$bundleId'"
        
        Set-Content $firebaseOptionsPath $content -NoNewline
        
        Write-Host "[OK] Successfully updated firebase_options.dart!" -ForegroundColor Green
        Write-Host ""
        
    } catch {
        Write-Host "[WARNING] Could not parse GoogleService-Info.plist automatically" -ForegroundColor Yellow
        Write-Host "Error: $($_.Exception.Message)" -ForegroundColor Red
        Write-Host "Please update lib/firebase_options.dart manually" -ForegroundColor Yellow
        Write-Host ""
    }
} else {
    Write-Host "[WARNING] GoogleService-Info.plist not found!" -ForegroundColor Yellow
    Write-Host "Expected location: ios\Runner\GoogleService-Info.plist" -ForegroundColor Yellow
    Write-Host "Please download it from Firebase Console" -ForegroundColor Yellow
    Write-Host ""
}

Write-Host "=====================================" -ForegroundColor Cyan
Write-Host "iOS Firebase Setup Complete!" -ForegroundColor Green
Write-Host "=====================================" -ForegroundColor Cyan
Write-Host ""
Write-Host "Next steps:" -ForegroundColor Cyan
Write-Host "  1. Both Android and iOS are now configured" -ForegroundColor White
Write-Host "  2. Run on iOS: flutter run -d ios" -ForegroundColor White
Write-Host "  3. Run on Android: flutter run -d android" -ForegroundColor White
Write-Host ""
