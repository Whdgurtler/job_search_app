import 'package:flutter/material.dart';

/// Placeholder login screen — will be implemented in Phase 3.
class LoginScreen extends StatelessWidget {
  const LoginScreen({super.key});

  @override
  Widget build(BuildContext context) {
    return Scaffold(
      body: Center(
        child: Column(
          mainAxisAlignment: MainAxisAlignment.center,
          children: [
            const Icon(Icons.work_outline, size: 80),
            const SizedBox(height: 24),
            Text(
              'Job Search Agent',
              style: Theme.of(context).textTheme.headlineMedium,
            ),
            const SizedBox(height: 48),
            const Text('Login screen — Phase 3'),
          ],
        ),
      ),
    );
  }
}
