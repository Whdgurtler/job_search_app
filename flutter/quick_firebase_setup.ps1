###############################################################################
# Quick Firebase Console Script
# Opens all necessary Firebase Console pages in your browser
###############################################################################

Write-Host "`n🔥 Firebase Quick Setup for Job Search Mobile`n" -ForegroundColor Cyan

# Create a new Firebase project in the console
Write-Host "Step 1: Creating Firebase Project..." -ForegroundColor Yellow
Start-Process "https://console.firebase.google.com/u/0/projects"
Start-Sleep -Seconds 2

Write-Host "`nIn the browser:" -ForegroundColor White
Write-Host "  1. Click 'Create a project' or 'Add project'" -ForegroundColor Gray
Write-Host "  2. Name: 'Job Search Mobile'" -ForegroundColor Gray  
Write-Host "  3. Accept terms and click Continue" -ForegroundColor Gray
Write-Host "  4. Disable Google Analytics (or keep it)" -ForegroundColor Gray
Write-Host "  5. Click 'Create project'`n" -ForegroundColor Gray

$continue = Read-Host "Press Enter after creating the project (or 'skip' if already created)"

if ($continue -ne "skip") {
    Start-Sleep -Seconds 2
}

# Get project ID
Write-Host "`n📋 What is your Firebase Project ID?" -ForegroundColor Yellow
Write-Host "   (Find it in the Project Settings, looks like: job-search-mobile-xxxxx)" -ForegroundColor Gray
$projectId = Read-Host "Enter Project ID"

if (-not $projectId) {
    $projectId = "job-search-mobile-app"
    Write-Host "Using default: $projectId" -ForegroundColor Gray
}

# Open project
$projectUrl = "https://console.firebase.google.com/u/0/project/$projectId"
Write-Host "`nOpening your project dashboard..." -ForegroundColor White
Start-Process $projectUrl
Start-Sleep -Seconds 2

# Enable Authentication
Write-Host "`nStep 2: Enable Authentication..." -ForegroundColor Yellow
Start-Process "$projectUrl/authentication/providers"
Start-Sleep -Seconds 1

Write-Host "`nIn the browser:" -ForegroundColor White
Write-Host "  1. Click 'Get started'" -ForegroundColor Gray
Write-Host "  2. Click 'Email/Password'" -ForegroundColor Gray
Write-Host "  3. Toggle 'Enable' ON" -ForegroundColor Gray
Write-Host "  4. Click 'Save'`n" -ForegroundColor Gray

Read-Host "Press Enter after enabling Email/Password authentication"

# Add Android App
Write-Host "`nStep 3: Add Android App..." -ForegroundColor Yellow
Start-Process "$projectUrl/settings/general"
Start-Sleep -Seconds 2

Write-Host "`nIn the browser (Project Settings):" -ForegroundColor White
Write-Host "  1. Scroll down and click the Android icon" -ForegroundColor Gray
Write-Host "  2. Package name: com.jobsearch.job_search_mobile" -ForegroundColor Cyan
Write-Host "  3. App nickname: Job Search Mobile Android" -ForegroundColor Gray
Write-Host "  4. Click 'Register app'" -ForegroundColor Gray
Write-Host "  5. Download 'google-services.json'" -ForegroundColor Green
Write-Host "  6. Save it to: android\app\google-services.json" -ForegroundColor Green
Write-Host "  7. Click through the remaining steps`n" -ForegroundColor Gray

Read-Host "Press Enter after downloading google-services.json"

# Add iOS App  
Write-Host "`nStep 4: Add iOS App (optional, for future iOS support)..." -ForegroundColor Yellow
Write-Host "`nIn the same Project Settings page:" -ForegroundColor White
Write-Host "  1. Click the iOS icon" -ForegroundColor Gray
Write-Host "  2. Bundle ID: com.jobsearch.mobile" -ForegroundColor Cyan
Write-Host "  3. App nickname: Job Search Mobile iOS" -ForegroundColor Gray
Write-Host "  4. Click 'Register app'" -ForegroundColor Gray
Write-Host "  5. Download 'GoogleService-Info.plist'" -ForegroundColor Green
Write-Host "  6. Save it to: ios\Runner\GoogleService-Info.plist" -ForegroundColor Green
Write-Host "  7. Click through the remaining steps`n" -ForegroundColor Gray

$ios = Read-Host "Press Enter if you added iOS, or type 'skip' to skip iOS"

# Get configuration values
Write-Host "`nStep 5: Get Firebase Configuration Values..." -ForegroundColor Yellow
Start-Process "$projectUrl/settings/general"

Write-Host "Open the downloaded google-services.json file and find these values:" -ForegroundColor White

if (Test-Path "android\app\google-services.json") {
    Write-Host "  [OK] Found google-services.json" -ForegroundColor Green
    
    try {
        $jsonContent = Get-Content "android\app\google-services.json" -Raw | ConvertFrom-Json
        $projectNumber = $jsonContent.project_info.project_number
        $projectId = $jsonContent.project_info.project_id
        $apiKey = $jsonContent.client[0].api_key[0].current_key
        $appId = $jsonContent.client[0].client_info.mobilesdk_app_id
        
        Write-Host "Extracted values from google-services.json:" -ForegroundColor Cyan
        Write-Host "  Project ID: $projectId" -ForegroundColor White
        Write-Host "  Sender ID: $projectNumber" -ForegroundColor White
        Write-Host "  API Key: $apiKey" -ForegroundColor White
        Write-Host "  App ID: $appId" -ForegroundColor White
        
        # Update firebase_options.dart automatically
        Write-Host "Updating lib/firebase_options.dart..." -ForegroundColor Yellow
        
        $firebaseOptions = Get-Content "lib\firebase_options.dart" -Raw
        $firebaseOptions = $firebaseOptions -replace "apiKey: 'YOUR_ANDROID_API_KEY'", "apiKey: '$apiKey'"
        $firebaseOptions = $firebaseOptions -replace "appId: '1:YOUR_APP_ID:android:YOUR_ANDROID_APP_ID'", "appId: '$appId'"
        $firebaseOptions = $firebaseOptions -replace "messagingSenderId: 'YOUR_SENDER_ID'", "messagingSenderId: '$projectNumber'"
        $firebaseOptions = $firebaseOptions -replace "projectId: 'YOUR_PROJECT_ID'", "projectId: '$projectId'"
        $firebaseOptions = $firebaseOptions -replace "'YOUR_PROJECT_ID.appspot.com'", "'$projectId.appspot.com'"
        
        Set-Content "lib\firebase_options.dart" $firebaseOptions
        
        Write-Host "  [OK] Android configuration updated!" -ForegroundColor Green
        
    } catch {
        Write-Host "  [WARNING] Could not parse google-services.json automatically" -ForegroundColor Yellow
        Write-Host "  Please update lib/firebase_options.dart manually" -ForegroundColor Yellow
    }
} else {
    Write-Host "  [WARNING] google-services.json not found in android/app/" -ForegroundColor Yellow
    Write-Host "  Please download it and place it there" -ForegroundColor Yellow
}

# Summary
Write-Host ""
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Firebase Setup Summary" -ForegroundColor Cyan
Write-Host "========================================" -ForegroundColor Cyan

Write-Host ""
Write-Host "Files to verify:" -ForegroundColor Yellow
$androidFile = Test-Path "android\app\google-services.json"
$iosFile = Test-Path "ios\Runner\GoogleService-Info.plist"

Write-Host "  [" -NoNewline
if ($androidFile) { Write-Host "X" -NoNewline -ForegroundColor Green } else { Write-Host "X" -NoNewline -ForegroundColor Red }
Write-Host "] android/app/google-services.json"

Write-Host "  [" -NoNewline
if ($iosFile) { Write-Host "X" -NoNewline -ForegroundColor Green } else { Write-Host "X" -NoNewline -ForegroundColor Yellow }
Write-Host "] ios/Runner/GoogleService-Info.plist"

Write-Host "  [" -NoNewline
Write-Host "X" -NoNewline -ForegroundColor Green
Write-Host "] lib/firebase_options.dart"

Write-Host ""
Write-Host "Next steps:" -ForegroundColor Yellow
Write-Host "  1. Run: flutter pub get" -ForegroundColor White
Write-Host "  2. Run: flutter run" -ForegroundColor White
Write-Host "  3. Test authentication (Sign Up/Sign In)" -ForegroundColor White

Write-Host ""
Write-Host "Setup complete! Happy coding!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "" -ForegroundColor White
