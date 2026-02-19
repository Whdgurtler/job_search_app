# Production Deployment Checklist

## 📋 Pre-Deployment Checklist

Use this checklist to ensure your app is ready for production deployment to Google Play Store and Apple App Store.

---

## 🔧 1. Development Setup

- [ ] **Flutter SDK** installed and up to date (`flutter doctor`)
- [ ] **Android Studio** / Xcode installed and configured
- [ ] All **dependencies** up to date (`flutter pub outdated`)
- [ ] **No errors** in code (`flutter analyze`)
- [ ] **Environment files** configured (`.env`, `.env.prod`)

---

## 🔐 2. Firebase Configuration

### Android
- [ ] **google-services.json** downloaded and placed in `android/app/`
- [ ] **firebase_options.dart** updated with Android credentials
- [ ] **Firebase Authentication** enabled (Email/Password)
- [ ] **Firebase project** permissions configured

### iOS
- [ ] **GoogleService-Info.plist** downloaded and placed in `ios/Runner/`
- [ ] **firebase_options.dart** updated with iOS credentials
- [ ] **Firebase Authentication** enabled for iOS
- [ ] **iOS bundle ID** registered in Firebase

**Scripts Available:**
- Run `.\setup_ios_firebase.ps1` for iOS setup
- Run `.\update_firebase_config.ps1` to verify Android config

---

## 🎨 3. App Branding

### App Icon
- [ ] **App icon** designed (1024x1024 PNG)
- [ ] Icon placed in `assets/icons/app_icon.png`
- [ ] **Adaptive icon foreground** created for Android
- [ ] Run `flutter pub run flutter_launcher_icons`
- [ ] Verify icon on device home screen

### Splash Screen
- [ ] **Splash logo** designed (1024x1024 PNG)
- [ ] Logo placed in `assets/splash/splash_logo.png`
- [ ] Dark mode variant created
- [ ] Run `flutter pub run flutter_native_splash:create`
- [ ] Test splash screen on device

**Scripts Available:**
- Run `.\create_placeholder_icon.ps1` for quick testing
- See `ICON_SPLASH_SETUP.md` for detailed instructions

---

## 🔑 4. Android Release Signing

- [ ] **Release keystore** generated
- [ ] **key.properties** file created
- [ ] Keystore file backed up securely
- [ ] Passwords stored in password manager
- [ ] `.gitignore` updated to exclude keystore files
- [ ] **ProGuard rules** configured in `android/app/proguard-rules.pro`
- [ ] Test build: `flutter build apk --release`

**Scripts Available:**
- Run `.\create_release_keystore.ps1` to generate signing key
- See `ANDROID_RELEASE_GUIDE.md` for detailed instructions

---

## 🔒 5. Security & Configuration

- [ ] **No hardcoded secrets** in code
- [ ] **API keys** in environment files, not committed
- [ ] **HTTPS only** for all API calls
- [ ] **Certificate pinning** configured (if required)
- [ ] **Debug mode** disabled in release builds
- [ ] **Logging** minimized or disabled in production
- [ ] **Error tracking** configured (Sentry/Firebase Crashlytics)

---

## 🌐 6. API & Backend

- [ ] **Production API URL** configured in `.env.prod`
- [ ] **API endpoints** tested and working
- [ ] **Authentication** working with production API
- [ ] **File uploads** (resume) tested
- [ ] **Error handling** for all API calls
- [ ] **Rate limiting** configured
- [ ] **CORS** configured for web (if applicable)

**Environment Setup:**
- Run `.\set_environment.ps1 -Environment production`
- See `ENVIRONMENT_CONFIG.md` for details

---

## ✅ 7. Testing

### Unit Tests
- [ ] Unit tests written for entities
- [ ] Unit tests for repositories
- [ ] Unit tests for business logic
- [ ] Run `flutter test test/unit/`

### Widget Tests
- [ ] Widget tests for critical screens
- [ ] Form validation tested
- [ ] Navigation tested
- [ ] Run `flutter test test/widget/`

### Integration Tests
- [ ] End-to-end user flows tested
- [ ] Authentication flow tested
- [ ] Job search and application flow tested
- [ ] Run integration tests

### Manual Testing
- [ ] Test on physical Android device
- [ ] Test on physical iOS device
- [ ] Test with different network conditions
- [ ] Test offline behavior
- [ ] Test with different screen sizes
- [ ] Test dark mode
- [ ] Test all user flows thoroughly

**Testing Guide:**
- See `TESTING_GUIDE.md` for comprehensive testing instructions

---

## 📱 8. Android Specific

### Build Configuration
- [ ] `applicationId` set correctly in `build.gradle.kts`
- [ ] `versionCode` and `versionName` updated in `pubspec.yaml`
- [ ] `minSdk` set to 21 (or higher)
- [ ] `targetSdk` set to latest
- [ ] **Release build** tested: `flutter build appbundle --release`

### Play Store Requirements
- [ ] **App icon** (512x512 PNG)
- [ ] **Feature graphic** (1024x500 PNG)
- [ ] **Screenshots** (2-8 images, phone and tablet)
- [ ] **Short description** (80 chars max)
- [ ] **Full description** (4000 chars max)
- [ ] **App category** selected
- [ ] **Content rating** questionnaire completed
- [ ] **Privacy policy** URL available
- [ ] **Contact email** configured

### Files to Upload
- [ ] `build/app/outputs/bundle/release/app-release.aab` (App Bundle)
- Or: `build/app/outputs/flutter-apk/app-release.apk` (APK)

---

## 🍎 9. iOS Specific

### Build Configuration
- [ ] **Bundle ID** set correctly
- [ ] **Version** and **Build number** updated
- [ ] **Apple Developer account** enrolled ($99/year)
- [ ] **Certificates** and **Provisioning Profiles** created
- [ ] **Xcode project** configured
- [ ] Test build: `flutter build ios --release`

### App Store Requirements
- [ ] **App icon** (1024x1024 PNG)
- [ ] **Screenshots** (multiple device sizes required)
  - 6.5" iPhone (1284 x 2778)
  - 5.5" iPhone (1242 x 2208)
  - iPad Pro (2048 x 2732)
- [ ] **App preview video** (optional but recommended)
- [ ] **App description** and **keywords**
- [ ] **Support URL** and **Marketing URL**
- [ ] **Privacy policy** URL
- [ ] **App Review information**

### App Store Connect
- [ ] App created in App Store Connect
- [ ] Bundle ID registered
- [ ] Screenshots uploaded
- [ ] App information filled
- [ ] Pricing and availability set
- [ ] Build uploaded via Xcode or Transporter

---

## 📄 10. Legal & Compliance

- [ ] **Privacy Policy** created and hosted
- [ ] **Terms of Service** created and hosted
- [ ] **GDPR compliance** (for EU users)
- [ ] **CCPA compliance** (for California users)
- [ ] **Children's privacy** compliance (if applicable)
- [ ] **Data retention** policy defined
- [ ] **Contact information** for legal inquiries

**Templates Available:**
- `PRIVACY_POLICY.md` - Customize with your details
- `TERMS_OF_SERVICE.md` - Customize with your details

**Action Required:**
- [ ] Host privacy policy on website
- [ ] Link to privacy policy in app settings
- [ ] Add contact email in both documents

---

## 📊 11. Analytics & Monitoring

- [ ] **Analytics** configured (Firebase Analytics, etc.)
- [ ] **Crash reporting** configured (Crashlytics, Sentry)
- [ ] **Performance monitoring** setup
- [ ] **User feedback** mechanism in place
- [ ] **App version tracking** implemented

---

## 🚀 12. Build & Upload

### Android
```powershell
# Set production environment
.\set_environment.ps1 -Environment production

# Build App Bundle (recommended)
flutter build appbundle --release

# Or build APK
flutter build apk --release

# Upload to Play Console
# https://play.google.com/console
```

### iOS
```bash
# Set production environment
.\set_environment.ps1 -Environment production

# Build iOS
flutter build ios --release

# Open Xcode and archive
open ios/Runner.xcworkspace

# Upload to App Store Connect via Xcode
```

---

## 📝 13. App Store Submission

### Google Play Console
1. Go to https://play.google.com/console
2. Create app or select existing app
3. Complete store listing:
   - Upload icon and graphics
   - Write descriptions
   - Add screenshots
4. Set content rating
5. Set pricing and distribution
6. Create release:
   - Production > Create new release
   - Upload `.aab` file
   - Write release notes
7. Review and rollout

### Apple App Store Connect
1. Go to https://appstoreconnect.apple.com
2. Create app or select existing app
3. Complete app information
4. Upload build via Xcode or Transporter
5. Add screenshots and descriptions
6. Set pricing and availability
7. Submit for review

---

## 🔄 14. Post-Deployment

- [ ] **Monitor crash reports** in first 24 hours
- [ ] **Check user reviews** and respond
- [ ] **Monitor performance** metrics
- [ ] **Address critical bugs** immediately
- [ ] **Plan next update** based on feedback

---

## 🆘 15. Troubleshooting

### Common Issues

**Build fails:**
- Run `flutter clean`
- Run `flutter pub get`
- Check `flutter doctor`
- Verify signing configuration

**App crashes:**
- Check ProGuard rules
- Review crash logs
- Test in release mode before submission

**Upload rejected:**
- Verify version code is higher than previous
- Check for policy violations
- Ensure all required assets uploaded

**Firebase not working:**
- Verify `google-services.json` / `GoogleService-Info.plist`
- Check Firebase project configuration
- Verify API keys in `firebase_options.dart`

---

## 📚 Documentation Reference

| Document | Purpose |
|----------|---------|
| [README.md](README.md) | Project overview |
| [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) | Development setup |
| [FIREBASE_SETUP.md](FIREBASE_SETUP.md) | Firebase configuration |
| [FIREBASE_MANUAL_SETUP.md](FIREBASE_MANUAL_SETUP.md) | Manual Firebase setup |
| [ANDROID_RELEASE_GUIDE.md](ANDROID_RELEASE_GUIDE.md) | Android release process |
| [ICON_SPLASH_SETUP.md](ICON_SPLASH_SETUP.md) | App icon and splash screen |
| [ENVIRONMENT_CONFIG.md](ENVIRONMENT_CONFIG.md) | Environment management |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | Testing instructions |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Code architecture |
| [PRIVACY_POLICY.md](PRIVACY_POLICY.md) | Privacy policy template |
| [TERMS_OF_SERVICE.md](TERMS_OF_SERVICE.md) | Terms of service template |

---

## ✨ Final Checklist

Before hitting "Submit for Review":

- [ ] All above sections completed
- [ ] App tested thoroughly on real devices
- [ ] Privacy policy and terms accessible
- [ ] Support email responds
- [ ] All store assets prepared
- [ ] Release notes written
- [ ] Team notified of submission
- [ ] Monitoring tools active
- [ ] Rollback plan prepared

---

## 🎉 You're Ready!

Once all items are checked, you're ready to deploy to production!

**Good luck with your app launch! 🚀**

---

**Need Help?**
- Review documentation in project root
- Run provided PowerShell scripts for automation
- Check [Flutter deployment docs](https://docs.flutter.dev/deployment)
- Contact support if needed
