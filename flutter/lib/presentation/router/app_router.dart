import 'package:flutter/material.dart';
import 'package:go_router/go_router.dart';
import '../screens/job_detail_screen.dart';
import '../screens/job_list_screen.dart';
import '../screens/login_screen.dart';
import '../screens/profile_screen.dart';
import '../screens/resume_upload_screen.dart';
import '../screens/scrape_screen.dart';
import '../screens/scrape_config_form_screen.dart';

class AppRouter {
  static GoRouter router(bool isAuthenticated) {
    return GoRouter(
      initialLocation: isAuthenticated ? '/jobs' : '/login',
      routes: [
        GoRoute(
          path: '/login',
          builder: (context, state) => const LoginScreen(),
        ),
        GoRoute(
          path: '/jobs',
          builder: (context, state) => const JobListScreen(),
        ),
        GoRoute(
          path: '/job/:id',
          builder: (context, state) {
            final id = state.pathParameters['id']!;
            return JobDetailScreen(jobId: id);
          },
        ),
        GoRoute(
          path: '/profile',
          builder: (context, state) => const ProfileScreen(),
        ),
        GoRoute(
          path: '/resume-upload',
          builder: (context, state) => const ResumeUploadScreen(),
        ),
        GoRoute(
          path: '/scrapes',
          builder: (context, state) => const ScrapeScreen(),
        ),
        GoRoute(
          path: '/scrapes/new-config',
          builder: (context, state) => const ScrapeConfigFormScreen(),
        ),
      ],
      redirect: (context, state) {
        final isLoginRoute = state.matchedLocation == '/login';

        if (!isAuthenticated && !isLoginRoute) {
          return '/login';
        }

        if (isAuthenticated && isLoginRoute) {
          return '/jobs';
        }

        return null;
      },
    );
  }
}
