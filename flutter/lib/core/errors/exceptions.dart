class AppException implements Exception {
  final String message;
  final int? statusCode;

  AppException(this.message, [this.statusCode]);

  @override
  String toString() => message;
}

class NetworkException extends AppException {
  NetworkException([String message = 'Network connection failed'])
      : super(message);
}

class ServerException extends AppException {
  ServerException([String message = 'Server error occurred', int? statusCode])
      : super(message, statusCode);
}

class AuthException extends AppException {
  AuthException([String message = 'Authentication failed'])
      : super(message);
}

class CacheException extends AppException {
  CacheException([String message = 'Cache operation failed'])
      : super(message);
}
