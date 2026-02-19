# Firebase Setup Instructions

Since the Firebase CLI requires manual PATH configuration, follow these steps to set up Firebase for your app:

## Option 1: Manual Firebase Console Setup (Recommended)

### Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project" or "Create a project"
3. Enter project name: **Job Search Mobile** (or your preferred name)
4. Project ID will be auto-generated (e.g., `job-search-mobile-xxxxx`)
5. Disable Google Analytics (optional)
6. Click "Create project"

### Step 2: Add Android App

1. In your Firebase project, click the Android icon
2. Enter package name: `com.jobsearch.job_search_mobile`
3. App nickname: "Job Search Mobile Android"
4. Click "Register app"
5. **Download `google-services.json`**
6. Place it in: `android/app/google-services.json`
7. Click "Next" through the remaining steps

### Step 3: Add iOS App

1. In your Firebase project, click the iOS icon
2. Enter bundle ID: `com.jobsearch.mobile`
3. App nickname: "Job Search Mobile iOS"
4. Click "Register app"
5. **Download `GoogleService-Info.plist`**
6. Place it in: `ios/Runner/GoogleService-Info.plist`
7. Click "Next" through the remaining steps

### Step 4: Enable Authentication

1. In Firebase Console, go to "Authentication"
2. Click "Get started"
3. Click on "Email/Password" under "Sign-in method"
4. Toggle "Enable"
5. Click "Save"

### Step 5: Update firebase_options.dart

After downloading the config files, update `lib/firebase_options.dart` with your actual Firebase configuration:

**For Android** (from google-services.json):
```dart
static const FirebaseOptions android = FirebaseOptions(
  apiKey: 'YOUR_API_KEY_FROM_GOOGLE_SERVICES_JSON',
  appId: 'YOUR_APP_ID_FROM_GOOGLE_SERVICES_JSON',
  messagingSenderId: 'YOUR_SENDER_ID',
  projectId: 'YOUR_PROJECT_ID',
  storageBucket: 'YOUR_PROJECT_ID.appspot.com',
);
```

**For iOS** (from GoogleService-Info.plist):
```dart
static const FirebaseOptions ios = FirebaseOptions(
  apiKey: 'YOUR_API_KEY_FROM_PLIST',
  appId: 'YOUR_APP_ID_FROM_PLIST',
  messagingSenderId: 'YOUR_SENDER_ID',
  projectId: 'YOUR_PROJECT_ID',
  storageBucket: 'YOUR_PROJECT_ID.appspot.com',
  iosBundleId: 'com.jobsearch.mobile',
);
```

### Step 6: Verify Android Configuration

The following files have already been configured:
- ✅ `android/build.gradle.kts` - Google services plugin added
- ✅ `android/app/build.gradle.kts` - Plugin applied, minSdk set to 21

Just ensure `google-services.json` is in `android/app/` directory.

### Step 7: Run the App

```bash
flutter pub get
flutter run
```

## Option 2: Using Firebase CLI (if available)

If you have Firebase CLI in your PATH, run:

```bash
# Add FlutterFire CLI to PATH
$env:Path += ";$env:LOCALAPPDATA\Pub\Cache\bin"

# Configure Firebase
flutterfire configure
```

Then select:
- Your Firebase project
- Platforms: Android, iOS
- This will auto-generate firebase_options.dart and download config files

## Troubleshooting

### Firebase CLI Not Found

If Firebase CLI is not recognized:

1. **Install via npm** (if Node.js is available):
   ```bash
   npm install -g firebase-tools
   firebase login
   ```

2. **Install standalone** (without Node.js):
   - Download from: https://firebase.google.com/docs/cli#windows-standalone-binary
   - Add to system PATH

3. **Use manual setup** (Option 1 above) - works without CLI

### Common Issues

**Error: "No Firebase App '[DEFAULT]'..."**
- Ensure `google-services.json` (Android) or `GoogleService-Info.plist` (iOS) are in correct locations
- Update `firebase_options.dart` with correct values

**Error: "Execution failed for task ':app:processDebugGoogleServices'"**
- Verify `google-services.json` is valid JSON
- Check package name matches: `com.jobsearch.job_search_mobile`

**Build fails with multidex error**
- Already configured with `multiDexEnabled = true` in build.gradle.kts

### Testing Authentication

Once setup is complete:

1. Run the app: `flutter run`
2. Click "Sign Up"
3. Enter email and password
4. Check Firebase Console > Authentication to see the new user

## Next Steps

After Firebase is configured:

1. ✅ Test authentication (sign up, sign in, sign out)
2. ✅ Ensure backend API is running at `http://localhost:8000`
3. ✅ For Android emulator, update `.env` to use `http://10.0.2.2:8000/api/v1`
4. ✅ For physical devices, use your computer's local IP address

## Configuration Files Checklist

- [ ] `google-services.json` → `android/app/google-services.json`
- [ ] `GoogleService-Info.plist` → `ios/Runner/GoogleService-Info.plist`
- [ ] `lib/firebase_options.dart` → Updated with your Firebase config
- [ ] Firebase Authentication → Email/Password enabled

## Quick Reference

**Package Name (Android):** `com.jobsearch.job_search_mobile`  
**Bundle ID (iOS):** `com.jobsearch.mobile`  
**Min SDK:** 21 (already configured)  
**Firebase Dependencies:** Already in pubspec.yaml

---

For detailed setup instructions, see [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)
