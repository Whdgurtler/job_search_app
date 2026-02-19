###############################################################################
# Firebase Setup Script for Job Search Mobile Flutter App
# Run this script in PowerShell after creating your Firebase project
###############################################################################

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Firebase Configuration for Flutter" -ForegroundColor Cyan
Write-Host "========================================`n" -ForegroundColor Cyan

# Step 1: Open Firebase Console
Write-Host "[Step 1] Opening Firebase Console..." -ForegroundColor Yellow
Write-Host "Please create a new project named 'Job Search Mobile'`n" -ForegroundColor White
Start-Process "https://console.firebase.google.com/"
Start-Sleep -Seconds 3

# Step 2: Instructions
Write-Host "[Step 2] Configure Firebase Project" -ForegroundColor Yellow
Write-Host @"
In the Firebase Console:
1. Click 'Add project' or 'Create a project'
2. Enter project name: Job Search Mobile
3. Disable/Enable Google Analytics as preferred
4. Click 'Create project'
5. Wait for project creation to complete
"@ -ForegroundColor White

Read-Host "`nPress Enter after creating the project..."

# Step 3: Add Android App
Write-Host "`n[Step 3] Add Android App" -ForegroundColor Yellow
Write-Host @"
1. Click the Android icon in your Firebase project
2. Enter package name: com.jobsearch.job_search_mobile
3. App nickname: Job Search Mobile Android
4. Click 'Register app'
5. Download google-services.json
6. Place it in: android/app/google-services.json
"@ -ForegroundColor White

Read-Host "`nPress Enter after downloading google-services.json..."

# Step 4: Add iOS App
Write-Host "`n[Step 4] Add iOS App" -ForegroundColor Yellow
Write-Host @"
1. Click the iOS icon in your Firebase project
2. Enter bundle ID: com.jobsearch.mobile
3. App nickname: Job Search Mobile iOS
4. Click 'Register app'
5. Download GoogleService-Info.plist
6. Place it in: ios/Runner/GoogleService-Info.plist
"@ -ForegroundColor White

Read-Host "`nPress Enter after downloading GoogleService-Info.plist..."

# Step 5: Enable Authentication
Write-Host "`n[Step 5] Enable Email/Password Authentication" -ForegroundColor Yellow
Write-Host @"
1. In Firebase Console, go to 'Authentication'
2. Click 'Get started'
3. Click on 'Email/Password' tab
4. Toggle 'Enable'
5. Click 'Save'
"@ -ForegroundColor White

$projectUrl = Read-Host "`nEnter your Firebase project URL (e.g., https://console.firebase.google.com/project/your-project-id)"

if ($projectUrl) {
    Start-Process "$projectUrl/authentication/providers"
}

Read-Host "`nPress Enter after enabling Email/Password authentication..."

# Step 6: Get Configuration Details
Write-Host "`n[Step 6] Get Firebase Configuration" -ForegroundColor Yellow
Write-Host "Opening project settings..." -ForegroundColor White

if ($projectUrl) {
    Start-Process "$projectUrl/settings/general"
}

Write-Host @"

For Android (from google-services.json):
- Find: "api_key" -> "current_key"
- Find: "mobilesdk_app_id"
- Find: "project_number" (messagingSenderId)
- Find: "project_id"

For iOS (from GoogleService-Info.plist):
- Find: API_KEY
- Find: GOOGLE_APP_ID
- Find: GCM_SENDER_ID (messagingSenderId)
- Find: PROJECT_ID
"@ -ForegroundColor Cyan

Read-Host "`nPress Enter to view the firebase_options.dart template..."

# Step 7: Display Configuration Template
Write-Host "`n[Step 7] Update lib/firebase_options.dart" -ForegroundColor Yellow
Write-Host @"

Replace the TODO sections in lib/firebase_options.dart with your values:

static const FirebaseOptions android = FirebaseOptions(
  apiKey: 'YOUR_ANDROID_API_KEY',              // from google-services.json
  appId: '1:YOUR_APP_ID:android:YOUR_HASH',    // from google-services.json
  messagingSenderId: 'YOUR_SENDER_ID',          // from google-services.json
  projectId: 'YOUR_PROJECT_ID',                 // from google-services.json
  storageBucket: 'YOUR_PROJECT_ID.appspot.com',
);

static const FirebaseOptions ios = FirebaseOptions(
  apiKey: 'YOUR_IOS_API_KEY',                  // from GoogleService-Info.plist
  appId: '1:YOUR_APP_ID:ios:YOUR_HASH',        // from GoogleService-Info.plist
  messagingSenderId: 'YOUR_SENDER_ID',          // from GoogleService-Info.plist
  projectId: 'YOUR_PROJECT_ID',                 // from GoogleService-Info.plist
  storageBucket: 'YOUR_PROJECT_ID.appspot.com',
  iosBundleId: 'com.jobsearch.mobile',
);

"@ -ForegroundColor Green

# Step 8: Verify Files
Write-Host "[Step 8] Verification Checklist" -ForegroundColor Yellow
$androidFile = Test-Path "android\app\google-services.json"
$iosFile = Test-Path "ios\Runner\GoogleService-Info.plist"

Write-Host "Checking files..." -ForegroundColor White
Write-Host "  android/app/google-services.json: " -NoNewline
if ($androidFile) {
    Write-Host "✓ Found" -ForegroundColor Green
} else {
    Write-Host "✗ Missing" -ForegroundColor Red
}

Write-Host "  ios/Runner/GoogleService-Info.plist: " -NoNewline
if ($iosFile) {
    Write-Host "✓ Found" -ForegroundColor Green
} else {
    Write-Host "✗ Missing (OK if only testing Android)" -ForegroundColor Yellow
}

# Step 9: Final Steps
Write-Host "`n[Step 9] Final Steps" -ForegroundColor Yellow
Write-Host @"
1. Update lib/firebase_options.dart with your Firebase config
2. Ensure google-services.json is in android/app/
3. Run: flutter pub get
4. Run: flutter run

"@ -ForegroundColor White

Write-Host "========================================" -ForegroundColor Cyan
Write-Host "Setup Complete!" -ForegroundColor Green
Write-Host "========================================" -ForegroundColor Cyan
Write-Host "`nFor troubleshooting, see FIREBASE_SETUP.md`n" -ForegroundColor White
