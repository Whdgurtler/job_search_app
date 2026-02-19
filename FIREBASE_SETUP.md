# Firebase Setup Guide

## Prerequisites
- Firebase account (free tier is sufficient)
- Flutter project created
- Firebase CLI installed (optional but recommended)

---

## Step 1: Create Firebase Project

1. Go to [Firebase Console](https://console.firebase.google.com/)
2. Click "Add project"
3. Enter project name: `job-search-agent` (or your preferred name)
4. Choose whether to enable Google Analytics (recommended for production)
5. Click "Create project"

---

## Step 2: Configure Authentication

1. In Firebase Console, navigate to **Authentication**
2. Click "Get started"
3. Enable **Email/Password** provider:
   - Click on "Email/Password"
   - Toggle "Enable" to ON
   - Toggle "Email link (passwordless sign-in)" to OFF (optional)
   - Click "Save"

---

## Step 3: Register Android App

1. In Firebase Console, click the Android icon (⚙️ > Project settings > Add app)
2. Enter Android package name:
   ```
   com.jobsearch.job_search_mobile
   ```
   (Must match the one in `android/app/build.gradle`)

3. Enter app nickname (optional): `Job Search Mobile - Android`
4. Enter debug signing certificate SHA-1 (required for Google Sign-In, optional for now)
   
   To get SHA-1:
   ```bash
   # Windows
   cd android
   gradlew signingReport
   
   # Look for SHA1 under "Variant: debug"
   ```

5. Click "Register app"
6. **Download `google-services.json`**
7. Place the file in:
   ```
   C:\job-search-agent\mobile\android\app\google-services.json
   ```

8. Follow the remaining setup steps in Firebase Console (dependencies should already be added)

---

## Step 4: Register iOS App

1. In Firebase Console, click the iOS icon (⚙️ > Project settings > Add app)
2. Enter iOS bundle ID:
   ```
   com.jobsearch.jobSearchMobile
   ```
   (Must match the one in `ios/Runner/Info.plist`)

3. Enter app nickname (optional): `Job Search Mobile - iOS`
4. Enter App Store ID (optional, for production)
5. Click "Register app"
6. **Download `GoogleService-Info.plist`**
7. Place the file in:
   ```
   C:\job-search-agent\mobile\ios\Runner\GoogleService-Info.plist
   ```

8. Follow the remaining setup steps in Firebase Console

---

## Step 5: Update Firebase Admin SDK (Backend)

The backend uses Firebase Admin SDK to verify tokens. Update the service account key:

1. In Firebase Console, go to **Project Settings > Service Accounts**
2. Click "Generate new private key"
3. Save the JSON file securely
4. Update backend configuration:

```bash
# Copy to backend directory
cp ~/Downloads/job-search-agent-firebase-adminsdk.json C:\job-search-agent\backend\firebase-service-account.json

# Update .env file
echo FIREBASE_CREDENTIALS_PATH=./firebase-service-account.json >> backend\.env
```

5. Update `backend/app/auth/firebase.py` if needed to load credentials

---

## Step 6: Verify Setup

### Test Android
```bash
cd C:\job-search-agent\mobile
flutter run -d <android-device-or-emulator>
```

### Test iOS (requires macOS)
```bash
cd C:\job-search-agent\mobile
flutter run -d <ios-device-or-simulator>
```

### Test Authentication
1. Launch the app
2. Sign up with a test email: `test@example.com` / `password123`
3. Check Firebase Console > Authentication > Users to see the new user
4. Check backend database:
   ```bash
   docker exec jobsearch_postgres psql -U jobsearch -d jobsearch -c "SELECT * FROM users;"
   ```
5. Verify the user appears in both Firebase and the backend database

---

## Common Issues

### Issue: "google-services.json not found"
**Solution**: Ensure the file is in `android/app/` (not `android/`)

### Issue: "GoogleService-Info.plist not found"
**Solution**: 
1. Open `ios/Runner.xcworkspace` in Xcode
2. Right-click on Runner folder
3. Add Files to "Runner"
4. Select `GoogleService-Info.plist`
5. Ensure "Copy items if needed" is checked

### Issue: "Firebase auth not working"
**Solution**: 
1. Ensure SHA-1 certificate is added (for Android)
2. Check that package name/bundle ID matches exactly
3. Run `flutter clean` and rebuild

### Issue: "Backend returns 401 Unauthorized"
**Solution**:
1. Verify Firebase service account JSON is in backend
2. Check that `FIREBASE_CREDENTIALS_PATH` is set correctly
3. Restart backend API server
4. Check backend logs for Firebase initialization errors

---

## Security Notes

1. **Never commit Firebase config files to Git**:
   ```bash
   # Add to .gitignore
   echo "android/app/google-services.json" >> .gitignore
   echo "ios/Runner/GoogleService-Info.plist" >> .gitignore
   echo "backend/firebase-service-account.json" >> .gitignore
   ```

2. **Use Firebase App Check** (recommended for production):
   - Protects backend API from abuse
   - Verifies requests come from your genuine app
   - Set up in Firebase Console > App Check

3. **Enable Firebase Security Rules** (if using Firestore/Storage later)

4. **Rotate service account keys** periodically

---

## Testing Without Firebase (Development)

If you want to test the app without setting up Firebase:

1. Update `backend/.env`:
   ```
   ENVIRONMENT=development
   ```

2. Backend will use dev mode auth bypass (returns test user)

3. Mobile app can skip auth temporarily:
   - Comment out Firebase initialization in `main.dart`
   - Hardcode test token in API service
   - **NOT RECOMMENDED** for anything beyond initial testing

---

## Next Steps After Setup

1. ✅ Test authentication flow end-to-end
2. ✅ Create test user and verify in both Firebase and backend
3. ✅ Test API calls from mobile app to backend
4. Configure Firebase Cloud Messaging (for push notifications)
5. Set up Firebase Analytics (optional)
6. Configure App Check for production

---

## Reference Links

- [Firebase Console](https://console.firebase.google.com/)
- [FlutterFire Documentation](https://firebase.flutter.dev/)
- [Firebase Admin SDK (Python)](https://firebase.google.com/docs/admin/setup)
- [Add Firebase to Android](https://firebase.google.com/docs/android/setup)
- [Add Firebase to iOS](https://firebase.google.com/docs/ios/setup)
