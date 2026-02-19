# Android Release Build Guide

## Prerequisites

1. **Java Development Kit (JDK)**
   - JDK 17 or later required
   - Check: `java -version`

2. **Android Debug Key (for testing)**
   - Automatically created by Flutter

3. **Release Keystore (for Play Store)**
   - Must be created (see setup below)

## Step 1: Create Release Keystore

Run the setup script:
```powershell
.\create_release_keystore.ps1
```

This will:
- Generate a keystore file: `android/app/upload-keystore.jks`
- Create configuration: `android/key.properties`
- Configure build.gradle.kts for release signing

### Manual Keystore Creation

If the script doesn't work, create manually:
```bash
keytool -genkeypair -v -keystore android/app/upload-keystore.jks \
  -storetype JKS -keyalg RSA -keysize 2048 -validity 10000 \
  -alias upload
```

Then create `android/key.properties`:
```properties
storePassword=your_store_password
keyPassword=your_key_password
keyAlias=upload
storeFile=upload-keystore.jks
```

## Step 2: Update .gitignore

Ensure these files are ignored (already configured):
```
/android/key.properties
/android/app/upload-keystore.jks
*.jks
```

## Step 3: Build Release APK

### Option A: APK (for direct distribution)
```bash
flutter build apk --release
```

Output: `build/app/outputs/flutter-apk/app-release.apk`

### Option B: App Bundle (recommended for Play Store)
```bash
flutter build appbundle --release
```

Output: `build/app/outputs/bundle/release/app-release.aab`

### Build with specific flavor
```bash
flutter build appbundle --release --flavor production
```

## Step 4: Test Release Build

Before uploading to Play Store, test the release build:

1. **Install APK on device:**
   ```bash
   adb install build/app/outputs/flutter-apk/app-release.apk
   ```

2. **Test thoroughly:**
   - Authentication flows
   - API connections
   - File uploads
   - All user flows
   - Performance

3. **Check for crashes:**
   - Monitor logcat: `adb logcat`
   - Test edge cases

## Step 5: Prepare for Play Store

### Required Assets:
- [ ] High-res icon (512x512)
- [ ] Feature graphic (1024x500)
- [ ] Screenshots (2-8 images)
  - Phone: 16:9 or 9:16 ratio
  - 7-inch tablet (optional)
  - 10-inch tablet (optional)

### App Information:
- [ ] Short description (80 chars max)
- [ ] Full description (4000 chars max)
- [ ] App category
- [ ] Content rating
- [ ] Privacy policy URL
- [ ] Contact email

### Upload to Play Console:
1. Go to https://play.google.com/console
2. Create app (if not exists)
3. Production > Create new release
4. Upload .aab file
5. Fill in release notes
6. Review and rollout

## Version Management

Update version in `pubspec.yaml`:
```yaml
version: 1.0.1+2
         #↑    ↑
         #│    └─ Build number (increment for each upload)
         #└────── Version name (visible to users)
```

Then rebuild.

## ProGuard Configuration

ProGuard is enabled for release builds. Rules are in:
`android/app/proguard-rules.pro`

If you encounter crashes in release mode:
1. Check ProGuard rules
2. Add keep rules for your models
3. Test thoroughly

## Common Issues

### Issue: "App not signed"
**Solution:** Ensure key.properties exists and is correctly configured

### Issue: "Unsigned APK"
**Solution:** Run `.\create_release_keystore.ps1` first

### Issue: "Build fails in release mode"
**Solution:** Check ProGuard rules, add exceptions for problematic classes

### Issue: "Release app crashes, debug works fine"
**Solution:** ProGuard may be removing required classes. Add keep rules.

### Issue: "Upload rejected by Play Store"
**Solution:** 
- Ensure version code is higher than previous
- Check for policy violations
- Verify all required assets uploaded

## Security Checklist

Before release:
- [ ] No hardcoded API keys or secrets
- [ ] Environment variables properly configured
- [ ] Debug mode disabled
- [ ] Keystore backed up securely
- [ ] key.properties not in version control
- [ ] Passwords stored in password manager
- [ ] HTTPS only for API calls
- [ ] Certificate pinning (if required)

## Build Variants (Future)

You can create build variants for different environments:
```kotlin
flavorDimensions += "environment"
productFlavors {
    create("development") {
        dimension = "environment"
        applicationIdSuffix = ".dev"
    }
    create("production") {
        dimension = "environment"
    }
}
```

Then build: `flutter build appbundle --flavor production`

## CI/CD Integration

For automated builds (GitHub Actions, Bitrise, etc.):
1. Store keystore as base64 in secrets
2. Store passwords in secrets
3. Decode keystore during build
4. Configure signing automatically

## Resources

- [Android App Signing](https://developer.android.com/studio/publish/app-signing)
- [Play Store Guidelines](https://play.google.com/about/developer-content-policy/)
- [Flutter Deployment](https://docs.flutter.dev/deployment/android)
