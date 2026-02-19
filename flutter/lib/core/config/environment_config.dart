import 'package:flutter_dotenv/flutter_dotenv.dart';

class EnvironmentConfig {
  static String get apiBaseUrl => dotenv.env['API_BASE_URL'] ?? 'http://localhost:8000/api/v1';
  static String get environment => dotenv.env['ENVIRONMENT'] ?? 'development';
  
  static bool get isDevelopment => environment == 'development';
  static bool get isProduction => environment == 'production';
}
