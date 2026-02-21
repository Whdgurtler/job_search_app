class AppConstants {
  // API Endpoints
  static const String loginEndpoint = '/auth/login';
  static const String registerEndpoint = '/auth/register';
  static const String jobsEndpoint = '/jobs';
  static const String jobDetailsEndpoint = '/jobs/{id}';
  static const String resumeUploadEndpoint = '/resumes/upload';
  static const String resumeListEndpoint = '/resumes';
  static const String companySuggestionsEndpoint = '/resumes/suggest-companies';
  static const String profileEndpoint = '/users/me';

  // Scrape Endpoints
  static const String scrapeConfigsEndpoint = '/scrape-configs';
  static const String scrapeConfigDetailEndpoint = '/scrape-configs/{id}';
  static const String scrapeTriggerEndpoint = '/scrapes/trigger';
  static const String scrapeRunsEndpoint = '/scrapes';
  static const String scrapeRunDetailEndpoint = '/scrapes/{id}';
  static const String scrapeRunStatusEndpoint = '/scrapes/{id}/status';

  // Storage Keys
  static const String tokenKey = 'auth_token';
  static const String userIdKey = 'user_id';
  static const String userEmailKey = 'user_email';

  // Timeouts
  static const Duration connectionTimeout = Duration(seconds: 30);
  static const Duration receiveTimeout = Duration(seconds: 30);
}
