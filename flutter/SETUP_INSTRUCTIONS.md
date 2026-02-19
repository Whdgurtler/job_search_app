# Setup Instructions

Follow these steps to set up and run the Job Search Mobile application.

## Prerequisites

Before you begin, ensure you have:
- ✅ Flutter SDK 3.11.0 or higher
- ✅ Dart SDK
- ✅ Android Studio (for Android development)
- ✅ Xcode (for iOS development, macOS only)
- ✅ Git
- ✅ A Firebase account
- ✅ A code editor (VS Code or Android Studio recommended)

## Step 1: Verify Flutter Installation

Check that Flutter is properly installed:

```bash
flutter --version
flutter doctor
```

Fix any issues reported by `flutter doctor`.

## Step 2: Install Dependencies

Install FlutterFire CLI globally:

```bash
dart pub global activate flutterfire_cli
```

Navigate to the project directory and install dependencies:

```bash
cd flutter
flutter pub get
```

## Step 3: Firebase Setup

### Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Enter project name: "Job Search Mobile" (or your preferred name)
4. Disable Google Analytics (optional)
5. Click "Create project"

### Enable Authentication

1. In Firebase Console, go to "Authentication"
2. Click "Get started"
3. Click on "Email/Password" under "Sign-in method"
4. Enable "Email/Password"
5. Click "Save"

### Configure Firebase for Flutter

Run the FlutterFire configuration:

```bash
flutterfire configure
```

This will:
- Prompt you to select your Firebase project
- Ask which platforms to configure (select Android and iOS)
- Generate `firebase_options.dart` automatically
- Update your Android and iOS configuration files

Follow the prompts:
1. Select your Firebase project from the list
2. Choose platforms: Android, iOS (use space to select, enter to confirm)
3. Wait for configuration to complete

## Step 4: Android Configuration

### Update build.gradle (if needed)

The FlutterFire CLI should have updated these automatically, but verify:

**android/build.gradle** should include:
```gradle
dependencies {
    classpath 'com.google.gms:google-services:4.4.0'
}
```

**android/app/build.gradle** should have:
```gradle
apply plugin: 'com.google.gms.google-services'

android {
    compileSdkVersion 34
    minSdkVersion 21
    targetSdkVersion 34
}
```

### MultiDex Support (if needed)

If your app exceeds the 64K method limit, add to **android/app/build.gradle**:

```gradle
android {
    defaultConfig {
        multiDexEnabled true
    }
}

dependencies {
    implementation 'androidx.multidex:multidex:2.0.1'
}
```

## Step 5: iOS Configuration (macOS only)

### Update minimum deployment target

Edit **ios/Podfile**:

```ruby
platform :ios, '13.0'
```

### Install CocoaPods dependencies

```bash
cd ios
pod install
cd ..
```

## Step 6: Environment Configuration

The environment files are already created. Update them if needed:

### Development (.env.dev)
```
API_BASE_URL=http://localhost:8000/api/v1
ENVIRONMENT=development
```

### Production (.env.prod)
```
API_BASE_URL=https://your-production-api.com/api/v1
ENVIRONMENT=production
```

**Important for Android Emulator:**
If testing on Android emulator, use `http://10.0.2.2:8000/api/v1` instead of `localhost`

**Important for Physical Devices:**
Use your computer's IP address instead of localhost (e.g., `http://192.168.1.100:8000/api/v1`)

## Step 7: Backend API Setup

Ensure your backend API is running at the configured URL (default: http://localhost:8000).

The app expects these endpoints:
- POST /auth/login
- POST /auth/register
- GET /jobs
- GET /jobs/{id}
- GET /profile
- PUT /profile
- POST /profile/resume
- DELETE /profile/resume

## Step 8: Run the Application

### For Android

```bash
flutter run -d Android
```

Or select Android device/emulator from your IDE.

### For iOS (macOS only)

```bash
flutter run -d iOS
```

Or select iOS simulator from your IDE.

### For specific environment

To use production environment, modify `main.dart` temporarily:

```dart
await dotenv.load(fileName: '.env.prod');
```

## Step 9: First Run

When you first run the app:

1. The app will start on the login screen
2. Click "Sign Up" to create a new account
3. Enter email and password
4. After sign up, you'll be redirected to the job list screen

## Troubleshooting

### Firebase Initialization Error

**Error:** "No Firebase App '[DEFAULT]' has been created"

**Solution:**
1. Run `flutterfire configure` again
2. Make sure `firebase_options.dart` exists in `lib/`
3. Restart the app

### Build Errors on Android

**Error:** "Execution failed for task ':app:processDebugGoogleServices'"

**Solution:**
1. Make sure `google-services.json` exists in `android/app/`
2. Run `flutterfire configure` if it's missing
3. Clean and rebuild: `flutter clean && flutter pub get`

### Build Errors on iOS

**Error:** CocoaPods not installed or outdated

**Solution:**
```bash
sudo gem install cocoapods
cd ios
pod install --repo-update
cd ..
```

### API Connection Issues

**Error:** "Network connection failed" or timeout errors

**Solution:**
1. Verify backend is running
2. For Android emulator, use `10.0.2.2` instead of `localhost`
3. For iOS simulator, `localhost` should work
4. For physical devices, use computer's IP address
5. Check firewall settings

### Code Generation Errors

**Error:** Missing .g.dart or .freezed.dart files

**Solution:**
```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

### Dependency Conflicts

**Solution:**
```bash
flutter clean
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
```

## Development Tips

### Hot Reload
Press `r` in the terminal or use IDE's hot reload button to see changes instantly.

### Hot Restart
Press `R` in the terminal or use IDE's hot restart button for a full restart.

### Debug Mode
The app runs in debug mode by default. Look for the debug banner in the top-right corner.

### Inspecting State
Use Flutter DevTools for debugging:
```bash
flutter pub global activate devtools
flutter pub global run devtools
```

### Viewing Logs
```bash
flutter logs
```

## Building for Release

### Android APK
```bash
flutter build apk --release
```

Output: `build/app/outputs/flutter-apk/app-release.apk`

### Android App Bundle (for Play Store)
```bash
flutter build appbundle --release
```

Output: `build/app/outputs/bundle/release/app-release.aab`

### iOS (requires macOS and Xcode)
```bash
flutter build ios --release
```

Then open `ios/Runner.xcworkspace` in Xcode to create archive.

## Next Steps

After successful setup:

1. ✅ Test authentication (sign up, sign in, sign out)
2. ✅ Browse job listings
3. ✅ View job details
4. ✅ Update profile information
5. ✅ Upload a test resume

## Additional Resources

- [Flutter Documentation](https://docs.flutter.dev/)
- [Firebase Documentation](https://firebase.google.com/docs)
- [Riverpod Documentation](https://riverpod.dev/)
- [Go Router Documentation](https://pub.dev/packages/go_router)

## Support

If you encounter issues not covered here:
1. Check the error messages carefully
2. Search for the error on Stack Overflow
3. Consult Flutter and Firebase documentation
4. Create an issue in the repository

Happy coding! 🚀
