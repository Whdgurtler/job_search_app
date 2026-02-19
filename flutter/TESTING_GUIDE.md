# Testing Guide

## Overview

This project uses Flutter's built-in testing framework along with additional packages for comprehensive testing coverage.

## Test Structure

```
test/
├── unit/               # Unit tests for business logic
│   ├── user_entity_test.dart
│   └── job_entity_test.dart
├── widget/             # Widget tests for UI components
│   └── login_screen_test.dart
└── integration/        # Integration tests for full workflows
    └── (to be added)
```

## Running Tests

### Run All Tests
```bash
flutter test
```

### Run Specific Test File
```bash
flutter test test/unit/user_entity_test.dart
```

### Run Tests with Coverage
```bash
flutter test --coverage
```

### View Coverage Report (Windows)
```powershell
# Generate HTML report
genhtml coverage/lcov.info -o coverage/html

# Open in browser
Start-Process coverage/html/index.html
```

## Test Types

### 1. Unit Tests

Test individual functions, methods, and classes in isolation.

**Location:** `test/unit/`

**Example:**
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:job_search_mobile/domain/entities/user_entity.dart';

void main() {
  group('UserEntity Tests', () {
    test('should create user with required fields', () {
      // Arrange & Act
      const user = UserEntity(
        id: '123',
        email: 'test@example.com',
        name: 'Test User',
        phoneNumber: '+1234567890',
      );

      // Assert
      expect(user.id, '123');
      expect(user.email, 'test@example.com');
    });
  });
}
```

**What to Test:**
- Entity creation and validation
- Data model transformations (toJson/fromJson)
- Business logic in use cases
- Repository implementations (with mocked data sources)
- Utility functions and helpers

### 2. Widget Tests

Test UI components and user interactions.

**Location:** `test/widget/`

**Example:**
```dart
import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

void main() {
  testWidgets('LoginScreen displays correctly', (WidgetTester tester) async {
    await tester.pumpWidget(
      const ProviderScope(
        child: MaterialApp(
          home: LoginScreen(),
        ),
      ),
    );

    expect(find.text('Welcome Back'), findsOneWidget);
    expect(find.byType(TextFormField), findsNWidgets(2));
  });
}
```

**What to Test:**
- Widget rendering
- User interactions (taps, text input)
- Form validation
- Navigation
- Loading states
- Error states

### 3. Integration Tests

Test complete user workflows across multiple screens.

**Location:** `test/integration/` or `integration_test/`

**Example:**
```dart
import 'package:flutter_test/flutter_test.dart';
import 'package:integration_test/integration_test.dart';

void main() {
  IntegrationTestWidgetsFlutterBinding.ensureInitialized();

  testWidgets('Complete authentication flow', (WidgetTester tester) async {
    // Test full login -> browse jobs -> apply workflow
  });
}
```

## Mocking Dependencies

### Using Mockito

1. **Add annotation:**
```dart
import 'package:mockito/annotations.dart';
import 'package:mockito/mockito.dart';

@GenerateMocks([AuthRepository, JobRepository])
import 'auth_provider_test.mocks.dart';
```

2. **Generate mocks:**
```bash
flutter pub run build_runner build
```

3. **Use in tests:**
```dart
void main() {
  late MockAuthRepository mockAuthRepository;

  setUp(() {
    mockAuthRepository = MockAuthRepository();
  });

  test('should sign in user', () async {
    // Arrange
    when(mockAuthRepository.signInWithEmailPassword(any, any))
        .thenAnswer((_) async => Right(testUser));

    // Act
    final result = await mockAuthRepository.signInWithEmailPassword(
      'test@example.com',
      'password',
    );

    // Assert
    expect(result.isRight(), true);
    verify(mockAuthRepository.signInWithEmailPassword(any, any)).called(1);
  });
}
```

## Test Coverage Goals

| Type | Target Coverage |
|------|----------------|
| Unit Tests | 80%+ |
| Widget Tests | 70%+ |
| Integration Tests | Key user flows |

## Best Practices

### 1. Follow the AAA Pattern
```dart
test('description', () {
  // Arrange - Set up test data and conditions
  final user = UserEntity(...);
  
  // Act - Execute the code being tested
  final result = user.copyWith(name: 'New Name');
  
  // Assert - Verify the results
  expect(result.name, 'New Name');
});
```

### 2. Use Descriptive Test Names
```dart
// ❌ Bad
test('test user', () { ... });

// ✅ Good
test('UserEntity copyWith should update specified fields only', () { ... });
```

### 3. Test One Thing Per Test
```dart
// ❌ Bad - Testing multiple things
test('user operations', () {
  expect(user.name, 'Name');
  expect(user.email, 'email');
  expect(user.copyWith(name: 'New'), ...);
});

// ✅ Good - Separate focused tests
test('should create user with correct name', () { ... });
test('should create user with correct email', () { ... });
test('copyWith should update name', () { ... });
```

### 4. Use Test Groups
```dart
group('UserEntity', () {
  group('creation', () {
    test('with required fields', () { ... });
    test('with optional fields', () { ... });
  });
  
  group('copyWith', () {
    test('should update single field', () { ... });
    test('should update multiple fields', () { ... });
  });
});
```

### 5. Setup and Teardown
```dart
group('AuthProvider', () {
  late AuthNotifier authNotifier;
  late MockAuthRepository mockRepo;

  setUp(() {
    mockRepo = MockAuthRepository();
    authNotifier = AuthNotifier(mockRepo);
  });

  tearDown(() {
    // Clean up resources
  });

  test('...', () { ... });
});
```

## Testing Riverpod Providers

### Option 1: ProviderContainer
```dart
test('auth provider state updates correctly', () async {
  final container = ProviderContainer(
    overrides: [
      authRepositoryProvider.overrideWithValue(mockAuthRepository),
    ],
  );

  // Test provider logic
  await container.read(authProvider.notifier).signIn('email', 'pass');
  
  expect(container.read(authProvider).user, isNotNull);
});
```

### Option 2: ProviderScope in Widget Tests
```dart
testWidgets('widget uses provider correctly', (tester) async {
  await tester.pumpWidget(
    ProviderScope(
      overrides: [
        jobProvider.overrideWith((ref) => mockJobProvider),
      ],
      child: MaterialApp(home: JobListScreen()),
    ),
  );
});
```

## Testing Async Code

```dart
test('async operation completes successfully', () async {
  // Use async/await
  final result = await repository.fetchJobs();
  expect(result.isRight(), true);
});

test('Stream emits correct values', () {
  // Test streams
  expect(
    stream,
    emitsInOrder([value1, value2, emitsDone]),
  );
});
```

## Testing Firebase

### Mock Firebase Auth
```dart
@GenerateMocks([FirebaseAuth, User, UserCredential])
import 'test.mocks.dart';

void main() {
  late MockFirebaseAuth mockAuth;

  setUp(() {
    mockAuth = MockFirebaseAuth();
  });

  test('sign in with Firebase', () async {
    when(mockAuth.signInWithEmailAndPassword(
      email: any,
      password: any,
    )).thenAnswer((_) async => mockUserCredential);

    // Test authentication logic
  });
}
```

## Golden Tests (Visual Regression)

Test widget appearance:
```dart
testWidgets('login screen golden test', (tester) async {
  await tester.pumpWidget(
    MaterialApp(home: LoginScreen()),
  );

  await expectLater(
    find.byType(LoginScreen),
    matchesGoldenFile('goldens/login_screen.png'),
  );
});
```

Update goldens:
```bash
flutter test --update-goldens
```

## Continuous Integration

### GitHub Actions Example
```yaml
name: Tests

on: [push, pull_request]

jobs:
  test:
    runs-on: ubuntu-latest
    steps:
      - uses: actions/checkout@v3
      - uses: subosito/flutter-action@v2
      - run: flutter pub get
      - run: flutter test --coverage
      - uses: codecov/codecov-action@v3
```

## Common Testing Patterns

### Test Fixtures
```dart
// test/fixtures/user_fixtures.dart
const testUser = UserEntity(
  id: '123',
  email: 'test@example.com',
  name: 'Test User',
  phoneNumber: '+1234567890',
);

const testJob = JobEntity(
  id: '1',
  title: 'Software Engineer',
  company: 'Tech Corp',
  // ...
);
```

### Test Helpers
```dart
// test/test_helpers.dart
Future<void> pumpLoginScreen(WidgetTester tester) async {
  await tester.pumpWidget(
    const ProviderScope(
      child: MaterialApp(home: LoginScreen()),
    ),
  );
}
```

## Debugging Tests

### Print Output
```dart
test('debug test', () {
  debugPrint('Value: $value');
  print('Another value: $other');
});
```

### Run Single Test
```bash
flutter test test/unit/user_entity_test.dart --name "should create user"
```

### VS Code Debugging
1. Set breakpoint in test file
2. Click "Debug" above test
3. Step through code

## Resources

- [Flutter Testing Documentation](https://docs.flutter.dev/testing)
- [Mockito Documentation](https://pub.dev/packages/mockito)
- [Integration Testing](https://docs.flutter.dev/testing/integration-tests)
- [Testing Riverpod](https://riverpod.dev/docs/cookbooks/testing)

## Next Steps

1. **Add more unit tests** for repositories and data sources
2. **Create widget tests** for all screens
3. **Add integration tests** for critical user flows
4. **Set up CI/CD** to run tests automatically
5. **Monitor test coverage** and improve weak areas
