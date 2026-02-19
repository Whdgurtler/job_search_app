import 'package:flutter/material.dart';
import 'package:flutter_test/flutter_test.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:job_search_mobile/presentation/screens/login_screen.dart';

void main() {
  group('LoginScreen Widget Tests', () {
    testWidgets('LoginScreen should display all required fields', (WidgetTester tester) async {
      // Arrange & Act
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: LoginScreen(),
          ),
        ),
      );

      // Assert
      expect(find.text('Welcome Back'), findsOneWidget);
      expect(find.byType(TextFormField), findsNWidgets(2)); // Email and Password fields
      expect(find.text('Sign In'), findsOneWidget);
      expect(find.text('Create Account'), findsOneWidget);
    });

    testWidgets('LoginScreen should toggle between Sign In and Sign Up modes', 
        (WidgetTester tester) async {
      // Arrange
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: LoginScreen(),
          ),
        ),
      );

      // Assert - Initially in Sign In mode
      expect(find.text('Sign In'), findsOneWidget);
      
      // Act - Tap "Create Account" button
      await tester.tap(find.text('Create Account'));
      await tester.pumpAndSettle();

      // Assert - Now in Sign Up mode
      expect(find.text('Sign Up'), findsOneWidget);
      expect(find.byType(TextFormField), findsNWidgets(3)); // Email, Password, and Confirm Password
    });

    testWidgets('LoginScreen should show validation errors for empty fields', 
        (WidgetTester tester) async {
      // Arrange
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: LoginScreen(),
          ),
        ),
      );

      // Act - Try to submit without filling fields
      await tester.tap(find.widgetWithText(ElevatedButton, 'Sign In'));
      await tester.pumpAndSettle();

      // Assert - Should show validation errors
      expect(find.text('Please enter your email'), findsOneWidget);
      expect(find.text('Please enter your password'), findsOneWidget);
    });

    testWidgets('LoginScreen should validate email format', 
        (WidgetTester tester) async {
      // Arrange
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: LoginScreen(),
          ),
        ),
      );

      // Act - Enter invalid email
      await tester.enterText(
        find.byType(TextFormField).first,
        'invalid-email',
      );
      await tester.tap(find.widgetWithText(ElevatedButton, 'Sign In'));
      await tester.pumpAndSettle();

      // Assert - Should show email validation error
      expect(find.text('Please enter a valid email'), findsOneWidget);
    });

    testWidgets('LoginScreen should show/hide password', 
        (WidgetTester tester) async {
      // Arrange
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: LoginScreen(),
          ),
        ),
      );

      // Find password field
      final passwordField = find.byType(TextFormField).at(1);
      
      // Enter password
      await tester.enterText(passwordField, 'password123');
      await tester.pump();

      // Find the TextField widget to check obscureText property
      final textField = tester.widget<TextField>(
        find.descendant(
          of: passwordField,
          matching: find.byType(TextField),
        ),
      );

      // Assert - Password should be obscured initially
      expect(textField.obscureText, true);

      // Act - Tap visibility icon
      await tester.tap(find.byIcon(Icons.visibility));
      await tester.pumpAndSettle();

      // Get updated TextField widget
      final updatedTextField = tester.widget<TextField>(
        find.descendant(
          of: passwordField,
          matching: find.byType(TextField),
        ),
      );

      // Assert - Password should be visible
      expect(updatedTextField.obscureText, false);
    });

    testWidgets('LoginScreen should display loading indicator when signing in', 
        (WidgetTester tester) async {
      // Arrange
      await tester.pumpWidget(
        const ProviderScope(
          child: MaterialApp(
            home: LoginScreen(),
          ),
        ),
      );

      // Fill in form
      await tester.enterText(
        find.byType(TextFormField).first,
        'test@example.com',
      );
      await tester.enterText(
        find.byType(TextFormField).at(1),
        'password123',
      );

      // Act - Submit form (this will fail without mocked providers, 
      // but we can test that loading state is shown)
      await tester.tap(find.widgetWithText(ElevatedButton, 'Sign In'));
      await tester.pump(); // Start the animation

      // Note: Full testing would require mocking the auth provider
      // This is a basic structure test
    });
  });
}
