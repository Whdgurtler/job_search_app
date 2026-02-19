# Job Search Mobile App

A production-ready Flutter mobile application for job searching with clean architecture, Firebase authentication, and REST API integration.

## 🚀 Status: Production Ready

This app is configured and ready for deployment to Google Play Store and Apple App Store.

## ✨ Features

- 🔐 **Firebase Authentication** - Email/Password sign-in and registration
- 📱 **Material Design 3 UI** - Modern, responsive design
- 🏗️ **Clean Architecture** - Separation of concerns (Presentation, Domain, Data)
- 🔄 **State Management** - Riverpod for predictable state handling
- 🌐 **REST API Client** - Dio with interceptors and error handling
- 📄 **Resume Upload** - File picking and resume management
- 👤 **User Profile** - Profile management with photo upload
- 🔍 **Job Search** - Browse and search job listings
- 📋 **Job Details** - Detailed job information and application
- 🌍 **Environment Config** - Dev/Staging/Production environment support
- 🔒 **Release Signing** - Android keystore configuration
- 🎨 **Custom Branding** - App icon and splash screen setup
- ✅ **Tested** - Unit and widget tests included

## 📁 Project Structure

```
lib/
├── core/
│   ├── config/          # Environment configuration
│   ├── constants/       # App constants
│   ├── errors/          # Error handling (Failures, Exceptions)
│   └── network/         # API client (Dio)
├── data/
│   ├── datasources/     # Remote data sources (Firebase, API)
│   ├── models/          # Data models (with Freezed)
│   └── repositories/    # Repository implementations
├── domain/
│   ├── entities/        # Business entities
│   └── repositories/    # Repository interfaces
└── presentation/
    ├── providers/       # Riverpod providers (Auth, Job, User)
    ├── router/          # App routing (Go Router)
    ├── screens/         # UI screens
    ├── theme/           # App theming (Material 3)
    └── widgets/         # Reusable widgets
```

## 🛠️ Getting Started

### Prerequisites

- **Flutter SDK** (>= 3.11.0)
- **Dart SDK**
- **Android Studio** / Xcode for mobile development
- **Firebase account** (for authentication)
- **Java JDK** 17+ (for Android release builds)

### Quick Setup
1. **Clone the repository**
   ```bash
   cd flutter
   ```

2. **Install dependencies**
   ```bash
   flutter pub get
   ```

3. **Setup Firebase** (Automated)
   
   For Android:
   ```powershell
   .\update_firebase_config.ps1
   ```
   
   For iOS:
   ```powershell
   .\setup_ios_firebase.ps1
   ```
   
   See [FIREBASE_MANUAL_SETUP.md](FIREBASE_MANUAL_SETUP.md) for manual setup instructions.

4. **Configure Environment**
   ```powershell
   # Use development environment (default)
   .\set_environment.ps1 -Environment development
   
   # Or use production environment
   .\set_environment.ps1 -Environment production
   ```

5. **Run the app**
   ```bash
   # Windows (requires Developer Mode enabled)
   flutter run -d windows
   
   # Android
   flutter run -d android
   
   # iOS (Mac only)
   flutter run -d ios
   ```

## 🚀 Production Deployment

### Complete Deployment Checklist

See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for comprehensive pre-deployment checklist.

### Quick Production Build

**Android (App Bundle for Play Store):**
```powershell
# Set production environment
.\set_environment.ps1 -Environment production

# Create release keystore (first time only)
.\create_release_keystore.ps1

# Build App Bundle
flutter build appbundle --release
```

**iOS (for App Store):**
```bash
# Set production environment
.\set_environment.ps1 -Environment production

# Build iOS
flutter build ios --release

# Archive and upload via Xcode
open ios/Runner.xcworkspace
```

### Store Requirements

- ✅ App icon and splash screen configured
- ✅ Release signing configured for Android
- ✅ Firebase authentication ready
- ✅ Environment configuration ready
- ✅ ProGuard rules configured
- ✅ Privacy policy and terms of service templates included
- ✅ Unit and widget tests included

## 📚 Documentation

| Document | Description |
|----------|-------------|
| [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) | Complete deployment checklist for stores |
| [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md) | Detailed development setup guide |
| [FIREBASE_SETUP.md](FIREBASE_SETUP.md) | Firebase configuration instructions |
| [ANDROID_RELEASE_GUIDE.md](ANDROID_RELEASE_GUIDE.md) | Android release build guide |
| [ICON_SPLASH_SETUP.md](ICON_SPLASH_SETUP.md) | App icon and splash screen setup |
| [ENVIRONMENT_CONFIG.md](ENVIRONMENT_CONFIG.md) | Environment management guide |
| [TESTING_GUIDE.md](TESTING_GUIDE.md) | Testing best practices |
| [PROJECT_STRUCTURE.md](PROJECT_STRUCTURE.md) | Code architecture details |
| [PRIVACY_POLICY.md](PRIVACY_POLICY.md) | Privacy policy template |
| [TERMS_OF_SERVICE.md](TERMS_OF_SERVICE.md) | Terms of service template |

## 🔧 Configuration Files

### Environment Files
- `.env` - Default development configuration
- `.env.dev` - Development environment
- `.env.staging` - Staging environment
- `.env.prod` - Production environment

### Firebase Configuration
- `lib/firebase_options.dart` - Firebase credentials
- `android/app/google-services.json` - Android Firebase config
- `ios/Runner/GoogleService-Info.plist` - iOS Firebase config

### Release Configuration
- `flutter_launcher_icons.yaml` - App icon configuration
- `flutter_native_splash.yaml` - Splash screen configuration
- `android/app/proguard-rules.pro` - ProGuard rules
- `android/key.properties` - Release signing keys (not in version control)

## 🌐 Environment Configuration

Switch between environments easily:

```powershell
# Development (localhost API)
.\set_environment.ps1 -Environment development

# Staging (staging API)
.\set_environment.ps1 -Environment staging

# Production (live API)
.\set_environment.ps1 -Environment production
```

Current environment variables:
- `API_BASE_URL` - Backend API base URL
- `ENVIRONMENT` - Current environment name

Add more variables in `.env` files and access via `EnvironmentConfig` class.

## 🧪 Testing

### Run All Tests
```bash
flutter test
```

### Run with Coverage
```bash
flutter test --coverage
```

### Test Files
- `test/unit/` - Unit tests for entities and business logic
- `test/widget/` - Widget tests for UI components
- `test/integration/` - End-to-end integration tests

See [TESTING_GUIDE.md](TESTING_GUIDE.md) for comprehensive testing documentation.

## 🔍 API Integration

The app connects to a REST API backend. Default URLs:

- **Development**: `http://localhost:8000/api/v1`
- **Staging**: `https://staging-api.jobsearch.com/api/v1`
- **Production**: `https://api.jobsearch.com/api/v1`

### API Endpoints Required:
- `POST /auth/login` - User login
- `POST /auth/register` - User registration
- `POST /auth/logout` - User logout
- `GET /jobs` - List jobs (with pagination, search, filters)
- `GET /jobs/{id}` - Get job details
- `POST /jobs/{id}/apply` - Apply for job
- `GET /profile` - Get user profile
- `PUT /profile` - Update user profile
- `POST /profile/resume` - Upload resume
- `DELETE /profile/resume` - Delete resume

## ✨ Features Details

### 🔐 Authentication
- Email/Password sign in and sign up
- Firebase Authentication integration
- Token-based API authentication
- Secure token storage with SharedPreferences
- Auto-login on app start
- Session management

### 🔍 Job Search
- Browse available jobs
- Search jobs by keywords
- Filter by location, type, experience level
- Pagination support
- Pull-to-refresh
- Infinite scroll loading
- Job bookmarking (coming soon)

### 📋 Job Details
- View comprehensive job information
- Company details and logo
- Salary range
- Required skills and qualifications
- Benefits
- Remote work indication
- Application button

### 👤 User Profile
- View and edit profile information
- Upload profile picture
- Upload resume (PDF, DOC, DOCX)
- Delete resume
- View applied jobs history
- Manage notifications preferences

### 🎨 UI/UX
- Material Design 3
- Light and dark mode support
- Responsive layouts for phone and tablet
- Custom app icons
- Branded splash screen
- Smooth animations and transitions

### 🏗️ Architecture
- **Clean Architecture** - Separation of concerns
- **Dependency Injection** - Using Riverpod
- **Repository Pattern** - Abstract data sources
- **Either Type** - Functional error handling with Dartz
- **Freezed Models** - Immutable data classes
- **Code Generation** - JSON serialization

## 🛠️ Development

### Code Generation

The app uses code generation for models and serialization:

```bash
# Run code generation
flutter pub run build_runner build --delete-conflicting-outputs

# Watch mode (auto-regenerate on file changes)
flutter pub run build_runner watch --delete-conflicting-outputs
```

### Hot Reload

Flutter supports hot reload during development:
- Press `r` in terminal to hot reload
- Press `R` to hot restart
- Press `q` to quit

### Debugging

Use VS Code or Android Studio:
1. Set breakpoints in code
2. Run app in debug mode
3. Use debug console for inspection

## 📦 Dependencies

### Core Packages
| Package | Purpose |
|---------|---------|
| `flutter_riverpod` | State management and dependency injection |
| `firebase_core` | Firebase SDK initialization |
| `firebase_auth` | User authentication |
| `dio` | HTTP client for API calls |
| `go_router` | Declarative routing |
| `shared_preferences` | Local key-value storage |
| `flutter_dotenv` | Environment configuration |
| `dartz` | Functional programming (Either type) |

### UI Packages
| Package | Purpose |
|---------|---------|
| `file_picker` | File selection (resume upload) |
| `image_picker` | Image selection (profile picture) |
| `flutter_svg` | SVG image support |
| `intl` | Internationalization and formatting |
| `cupertino_icons` | iOS-style icons |

### Development Packages
| Package | Purpose |
|---------|---------|
| `freezed` | Code generation for immutable classes |
| `json_serializable` | JSON serialization |
| `build_runner` | Code generation runner |
| `flutter_lints` | Linting rules |
| `mockito` | Mocking for tests |
| `flutter_launcher_icons` | Generate app icons |
| `flutter_native_splash` | Generate splash screens |

## 🔧 Scripts

PowerShell scripts for common tasks:

| Script | Purpose |
|--------|---------|
| `set_environment.ps1` | Switch between dev/staging/prod environments |
| `create_release_keystore.ps1` | Generate Android release signing key |
| `update_firebase_config.ps1` | Update Android Firebase configuration |
| `setup_ios_firebase.ps1` | Setup iOS Firebase configuration |
| `create_placeholder_icon.ps1` | Generate placeholder app icon |

Usage:
```powershell
.\set_environment.ps1 -Environment production
```

## 🐛 Troubleshooting

### Firebase Configuration Issues
**Problem:** Firebase not connecting

**Solution:**
1. Verify `google-services.json` is in `android/app/`
2. Verify `GoogleService-Info.plist` is in `ios/Runner/`
3. Check `firebase_options.dart` has correct credentials
4. Run `.\update_firebase_config.ps1` to re-sync Android config

### API Connection Issues
**Problem:** Can't connect to localhost API

**Solution:**
- **Android Emulator**: Use `http://10.0.2.2:8000/api/v1`
- **iOS Simulator**: Use `http://localhost:8000/api/v1`
- **Physical Device**: Use your computer's IP (e.g., `http://192.168.1.100:8000/api/v1`)

Update in `.env`:
```
API_BASE_URL=http://10.0.2.2:8000/api/v1
```

### Code Generation Issues
**Problem:** Missing `.g.dart` or `.freezed.dart` files

**Solution:**
```bash
flutter clean
flutter pub get
flutter pub run build_runner build --delete-conflicting-outputs
```

### Build Issues
**Problem:** Build fails

**Solution:**
1. Run `flutter clean`
2. Run `flutter pub get`
3. Check `flutter doctor` for issues
4. Verify signing configuration (Android)
5. Check Xcode configuration (iOS)

### Windows Developer Mode Required
**Problem:** "Building with plugins requires symlink support"

**Solution:**
1. Run `start ms-settings:developers`
2. Enable "Developer Mode"
3. Restart and rebuild

## 📄 Legal

### Privacy Policy & Terms of Service

Templates are provided in:
- [PRIVACY_POLICY.md](PRIVACY_POLICY.md)
- [TERMS_OF_SERVICE.md](TERMS_OF_SERVICE.md)

**Action Required Before Deployment:**
1. Customize with your company information
2. Add your contact details
3. Host on a public URL
4. Link from app settings screen
5. Reference in store listings

## 🤝 Contributing

1. Fork the repository
2. Create a feature branch
3. Make your changes
4. Add tests
5. Run `flutter analyze` and `flutter test`
6. Submit a pull request

## 📝 Version History

- **1.0.0+1** - Initial production-ready release
  - Firebase authentication
  - Job search and browsing
  - User profiles and resume upload
  - Material Design 3 UI
  - Environment configuration
  - Release signing configured

## 🎯 Roadmap

### Planned Features
- [ ] Social authentication (Google, Apple)
- [ ] Job bookmarking and saved searches
- [ ] Push notifications for new jobs
- [ ] In-app chat with employers
- [ ] Advanced filters and search
- [ ] Job application tracking
- [ ] Dark mode improvements
- [ ] Accessibility enhancements

### Technical Improvements
- [ ] Integration tests
- [ ] CI/CD pipeline
- [ ] Automated deployments
- [ ] Analytics integration
- [ ] Crash reporting (Sentry/Crashlytics)
- [ ] Performance monitoring
- [ ] Code coverage > 80%

## 📞 Support

For questions, issues, or feature requests:

- **Documentation**: Check the comprehensive guides in the repository
- **Issues**: Create an issue on GitHub
- **Email**: [INSERT YOUR SUPPORT EMAIL]

## 📜 License

This project is licensed under [INSERT YOUR LICENSE] - see the LICENSE file for details.

## 🙏 Acknowledgments

- Flutter team for the amazing framework
- Firebase for authentication and backend services
- Riverpod for elegant state management
- The open-source community

---

**Ready to deploy?** See [DEPLOYMENT_CHECKLIST.md](DEPLOYMENT_CHECKLIST.md) for the complete checklist!

**Happy coding! 🚀**