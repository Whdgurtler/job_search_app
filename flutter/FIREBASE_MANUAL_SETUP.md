# Firebase Manual Setup Guide

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click **"Add project"** or **"Create a project"**
3. Enter project name: `job-search-mobile`
4. Click **Continue**
5. Disable Google Analytics (optional) or keep it enabled
6. Click **Create project**
7. Wait for project creation to complete
8. Click **Continue** to go to project dashboard

## Step 2: Enable Email/Password Authentication

1. In the left sidebar, click **"Authentication"**
2. Click **"Get started"**
3. Click on **"Email/Password"** provider
4. Toggle **"Enable"** to ON
5. Click **"Save"**

## Step 3: Register Android App

1. In the left sidebar, click the **gear icon** ⚙️ next to "Project Overview"
2. Click **"Project settings"**
3. Scroll down to "Your apps" section
4. Click the **Android icon** 🤖
5. Enter the following details:
   - **Android package name**: `com.jobsearch.job_search_mobile`
   - **App nickname**: `Job Search Mobile` (optional)
   - **Debug signing certificate SHA-1**: Leave blank for now
6. Click **"Register app"**
7. Click **"Download google-services.json"**
8. Save the file to: `c:\job-search-agent\flutter\android\app\google-services.json`
9. Click **"Next"** through the remaining steps
10. Click **"Continue to console"**

## Step 4: Register iOS App (Optional)

1. In Project Settings, scroll down to "Your apps"
2. Click the **Apple icon** 🍎
3. Enter the following details:
   - **iOS bundle ID**: `com.jobsearch.mobile`
   - **App nickname**: `Job Search Mobile iOS` (optional)
4. Click **"Register app"**
5. Click **"Download GoogleService-Info.plist"**
6. Save the file to: `c:\job-search-agent\flutter\ios\Runner\GoogleService-Info.plist`
7. Click **"Next"** through the remaining steps
8. Click **"Continue to console"**

## Step 5: Update Firebase Options

After downloading `google-services.json`, run this PowerShell script to automatically update your Firebase configuration:

```powershell
# Navigate to project directory
cd c:\job-search-agent\flutter

# Run the update script
.\update_firebase_config.ps1
```

## Verification

After setup, verify the files exist:
- ✅ `android\app\google-services.json`
- ✅ `ios\Runner\GoogleService-Info.plist` (if iOS setup)
- ✅ `lib\firebase_options.dart` (updated with real values)

## Troubleshooting

**Project ID Format**: Your Firebase project ID will look like `job-search-mobile-a1b2c` (with random characters appended)

**Permission Issues**: Make sure you're logged in with the correct Google account that has project creation permissions

**File Locations**: Ensure files are in the exact paths specified above
