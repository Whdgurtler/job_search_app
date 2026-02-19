# Project Structure

This document provides an overview of the complete file structure of the Job Search Mobile application.

## Root Directory

```
job_search_mobile/
├── android/                    # Android native code
├── ios/                        # iOS native code
├── lib/                        # Main application code
├── assets/                     # Static assets
├── test/                       # Test files
├── .env                        # Default environment file
├── .env.dev                    # Development environment
├── .env.prod                   # Production environment
├── .gitignore                  # Git ignore rules
├── pubspec.yaml                # Dependencies and project config
├── README.md                   # Project documentation
├── SETUP_INSTRUCTIONS.md       # Setup guide
└── PROJECT_STRUCTURE.md        # This file
```

## Application Code (lib/)

### Core Layer
Contains shared functionality used across the app.

```
lib/core/
├── config/
│   └── environment_config.dart         # Environment configuration
├── constants/
│   └── app_constants.dart              # App-wide constants
├── errors/
│   ├── exceptions.dart                 # Exception classes
│   └── failures.dart                   # Failure classes
└── network/
    └── dio_client.dart                 # HTTP client wrapper
```

### Domain Layer
Business logic and abstract definitions (framework-independent).

```
lib/domain/
├── entities/
│   ├── job_entity.dart                 # Job entity
│   ├── job_entity.freezed.dart         # Generated freezed code
│   ├── job_entity.g.dart               # Generated JSON code
│   ├── user_entity.dart                # User entity
│   ├── user_entity.freezed.dart        # Generated freezed code
│   └── user_entity.g.dart              # Generated JSON code
└── repositories/
    ├── auth_repository.dart            # Auth repository interface
    ├── job_repository.dart             # Job repository interface
    └── user_repository.dart            # User repository interface
```

### Data Layer
Implementation of domain layer interfaces and external data sources.

```
lib/data/
├── datasources/
│   ├── auth_remote_data_source.dart    # Firebase auth data source
│   ├── job_remote_data_source.dart     # Job API data source
│   └── user_remote_data_source.dart    # User API data source
├── models/
│   ├── job_model.dart                  # Job data model
│   ├── job_model.freezed.dart          # Generated freezed code
│   ├── job_model.g.dart                # Generated JSON code
│   ├── user_model.dart                 # User data model
│   ├── user_model.freezed.dart         # Generated freezed code
│   └── user_model.g.dart               # Generated JSON code
└── repositories/
    ├── auth_repository_impl.dart       # Auth repository implementation
    ├── job_repository_impl.dart        # Job repository implementation
    └── user_repository_impl.dart       # User repository implementation
```

### Presentation Layer
UI components, state management, and routing.

```
lib/presentation/
├── providers/
│   ├── providers.dart                  # Core providers (DI)
│   ├── auth_provider.dart              # Authentication state
│   ├── job_provider.dart               # Job state management
│   └── user_provider.dart              # User profile state
├── router/
│   └── app_router.dart                 # App navigation routes
├── screens/
│   ├── login_screen.dart               # Login/signup screen
│   ├── job_list_screen.dart            # Job listing screen
│   ├── job_detail_screen.dart          # Job details screen
│   ├── profile_screen.dart             # User profile screen
│   └── resume_upload_screen.dart       # Resume upload screen
├── theme/
│   └── app_theme.dart                  # Material Design 3 theme
└── widgets/
    └── job_card.dart                   # Reusable job card widget
```

### Main Entry Point

```
lib/
├── main.dart                           # Application entry point
└── firebase_options.dart               # Firebase configuration
```

## Key Files Description

### Configuration Files

- **pubspec.yaml**: Defines dependencies, assets, and project metadata
- **.env**: Environment variables for development
- **.env.dev**: Development-specific configuration
- **.env.prod**: Production-specific configuration
- **.gitignore**: Specifies files to ignore in version control

### Core Files

- **environment_config.dart**: Manages environment-specific settings
- **app_constants.dart**: Defines API endpoints, timeouts, storage keys
- **dio_client.dart**: Configures HTTP client with interceptors

### Domain Files

- **entities/**: Immutable business objects
- **repositories/**: Abstract interfaces for data operations

### Data Files

- **datasources/**: Direct interaction with external APIs/services
- **models/**: Data transfer objects with JSON serialization
- **repositories/**: Concrete implementations of domain repositories

### Presentation Files

- **providers/**: Riverpod state management providers
- **screens/**: Full-page UI components
- **widgets/**: Reusable UI components
- **router/**: Navigation configuration
- **theme/**: App theming and styling

## Architecture Flow

```
┌─────────────────────────────────────────────────────────┐
│                    Presentation Layer                    │
│  ┌─────────────┐  ┌──────────┐  ┌───────────────────┐  │
│  │   Screens   │  │ Providers │  │  Widgets & Theme  │  │
│  └─────────────┘  └──────────┘  └───────────────────┘  │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                     Domain Layer                         │
│  ┌──────────────┐  ┌──────────────────────────────┐    │
│  │   Entities   │  │  Repository Interfaces       │    │
│  └──────────────┘  └──────────────────────────────┘    │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│                      Data Layer                          │
│  ┌─────────────┐  ┌─────────────┐  ┌──────────────┐   │
│  │   Models    │  │ Data Sources │  │ Repositories │   │
│  └─────────────┘  └─────────────┘  └──────────────┘   │
└────────────────────────┬────────────────────────────────┘
                         │
┌────────────────────────▼────────────────────────────────┐
│              External Services                           │
│  ┌──────────────────┐  ┌─────────────────────────┐     │
│  │  Firebase Auth   │  │   REST API Backend      │     │
│  └──────────────────┘  └─────────────────────────┘     │
└─────────────────────────────────────────────────────────┘
```

## Dependency Flow

- **Presentation** depends on **Domain** and **Data**
- **Data** implements **Domain** interfaces
- **Domain** is independent (core business logic)

## Code Generation

The following files are auto-generated:

- `*.g.dart` - JSON serialization code
- `*.freezed.dart` - Immutable classes with freezed

Generate with:
```bash
flutter pub run build_runner build --delete-conflicting-outputs
```

## Testing Structure (Future Enhancement)

```
test/
├── unit/
│   ├── domain/
│   └── data/
├── widget/
└── integration/
```

## Additional Notes

### State Management
- Uses **Riverpod** for dependency injection and state management
- Providers are organized by feature (auth, jobs, user)
- State classes use copyWith pattern for immutability

### Navigation
- **go_router** for declarative routing
- Route protection based on authentication state
- Deep linking support ready

### Error Handling
- Custom exception classes for different error types
- Failures for domain layer
- Exceptions for data layer
- User-friendly error messages in UI

### Data Persistence
- **SharedPreferences** for token storage
- **Firebase Auth** for authentication state
- API caching not implemented (future enhancement)

### API Communication
- **Dio** for HTTP requests
- Automatic token injection via interceptors
- Error handling and transformation
- Support for file uploads

## Environment Variables

Used environment variables:
- `API_BASE_URL` - Backend API URL
- `ENVIRONMENT` - Current environment (dev/prod)

## Assets

Place static assets in:
- `assets/images/` - Image files
- `assets/icons/` - Icon files
- `assets/fonts/` - Custom fonts

Remember to declare in `pubspec.yaml` under `flutter: assets:`

## Platform-Specific Code

### Android
- `android/app/src/main/AndroidManifest.xml` - Permissions, app config
- `android/app/build.gradle` - Dependencies, versions
- `android/app/google-services.json` - Firebase config

### iOS
- `ios/Runner/Info.plist` - Permissions, app config
- `ios/Podfile` - CocoaPods dependencies
- `ios/Runner/GoogleService-Info.plist` - Firebase config

## Best Practices Followed

1. **Clean Architecture** - Separation of concerns
2. **SOLID Principles** - Maintainable code structure
3. **Dependency Injection** - Testable components
4. **Immutability** - Using freezed for entities/models
5. **Type Safety** - Leveraging Dart's type system
6. **Error Handling** - Consistent error management
7. **Code Generation** - Reducing boilerplate

## Future Enhancements

Potential additions:
- Local database (Hive/SQLite) for offline support
- Push notifications
- Unit and integration tests
- Localization (i18n)
- Analytics integration
- Advanced search filters
- Job application tracking
- Saved jobs/favorites
- Dark mode toggle

---

For setup instructions, see [SETUP_INSTRUCTIONS.md](SETUP_INSTRUCTIONS.md)
For general information, see [README.md](README.md)
