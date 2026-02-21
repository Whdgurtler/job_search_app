import 'package:dio/dio.dart';
import '../../core/constants/app_constants.dart';
import '../../core/errors/exceptions.dart';
import '../../core/network/dio_client.dart';
import '../../domain/entities/scrape_entity.dart';

abstract class ScrapeRemoteDataSource {
  Future<List<ScrapeConfigEntity>> getConfigs();
  Future<ScrapeConfigEntity> createConfig(Map<String, dynamic> data);
  Future<void> deleteConfig(String configId);
  Future<ScrapeRunEntity> triggerScrape(Map<String, dynamic> data);
  Future<List<ScrapeRunEntity>> getRuns();
  Future<ScrapeRunStatusEntity> getRunStatus(String runId);
  Future<List<CompanySuggestion>> getCompanySuggestions();
}

class CompanySuggestion {
  final String name;
  final String reason;

  CompanySuggestion({required this.name, required this.reason});
}

class ScrapeRemoteDataSourceImpl implements ScrapeRemoteDataSource {
  final DioClient _client;

  ScrapeRemoteDataSourceImpl(this._client);

  @override
  Future<List<ScrapeConfigEntity>> getConfigs() async {
    try {
      final response = await _client.get(AppConstants.scrapeConfigsEndpoint);
      if (response.statusCode == 200) {
        final List<dynamic> data = response.data is List ? response.data : (response.data['data'] ?? []);
        return data.map((json) => _configFromJson(json)).toList();
      }
      throw ServerException('Failed to fetch configs', response.statusCode);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  @override
  Future<ScrapeConfigEntity> createConfig(Map<String, dynamic> data) async {
    try {
      final response = await _client.post(AppConstants.scrapeConfigsEndpoint, data: data);
      if (response.statusCode == 201 || response.statusCode == 200) {
        return _configFromJson(response.data);
      }
      throw ServerException('Failed to create config', response.statusCode);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  @override
  Future<void> deleteConfig(String configId) async {
    try {
      final endpoint = AppConstants.scrapeConfigDetailEndpoint.replaceAll('{id}', configId);
      await _client.delete(endpoint);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  @override
  Future<ScrapeRunEntity> triggerScrape(Map<String, dynamic> data) async {
    try {
      final response = await _client.post(AppConstants.scrapeTriggerEndpoint, data: data);
      if (response.statusCode == 202 || response.statusCode == 200) {
        return _runFromJson(response.data);
      }
      throw ServerException('Failed to trigger scrape', response.statusCode);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  @override
  Future<List<ScrapeRunEntity>> getRuns() async {
    try {
      final response = await _client.get(AppConstants.scrapeRunsEndpoint);
      if (response.statusCode == 200) {
        final List<dynamic> data = response.data is List ? response.data : (response.data['data'] ?? []);
        return data.map((json) => _runFromJson(json)).toList();
      }
      throw ServerException('Failed to fetch runs', response.statusCode);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  @override
  Future<ScrapeRunStatusEntity> getRunStatus(String runId) async {
    try {
      final endpoint = AppConstants.scrapeRunStatusEndpoint.replaceAll('{id}', runId);
      final response = await _client.get(endpoint);
      if (response.statusCode == 200) {
        final json = response.data;
        return ScrapeRunStatusEntity(
          id: json['id'],
          status: json['status'],
          progress: json['progress'],
          totalJobs: json['total_jobs'] ?? 0,
          newJobs: json['new_jobs'] ?? 0,
          durationSeconds: (json['duration_seconds'] ?? 0).toDouble(),
        );
      }
      throw ServerException('Failed to fetch run status', response.statusCode);
    } on DioException catch (e) {
      throw _handleDioError(e);
    }
  }

  @override
  Future<List<CompanySuggestion>> getCompanySuggestions() async {
    try {
      final response = await _client.get(AppConstants.companySuggestionsEndpoint);
      if (response.statusCode == 200) {
        final List<dynamic> suggestions = response.data['suggestions'] ?? [];
        return suggestions
            .map((s) => CompanySuggestion(
                  name: s['name'] ?? '',
                  reason: s['reason'] ?? '',
                ))
            .where((s) => s.name.isNotEmpty)
            .toList();
      }
      return [];
    } on DioException {
      return [];
    }
  }

  ScrapeConfigEntity _configFromJson(Map<String, dynamic> json) {
    return ScrapeConfigEntity(
      id: json['id'],
      name: json['name'] ?? '',
      keywords: json['keywords'] ?? '',
      companies: (json['companies'] as List<dynamic>?)?.cast<String>(),
      employmentAreas: (json['employment_areas'] as List<dynamic>?)?.cast<String>(),
      location: json['location'] ?? '',
      isDefault: json['is_default'] ?? false,
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  ScrapeRunEntity _runFromJson(Map<String, dynamic> json) {
    return ScrapeRunEntity(
      id: json['id'],
      status: json['status'] ?? 'pending',
      scrapedDate: json['scraped_date'] ?? '',
      companies: (json['companies'] as List<dynamic>?)?.cast<String>(),
      keywords: json['keywords'] ?? '',
      totalJobs: json['total_jobs'] ?? 0,
      newJobs: json['new_jobs'] ?? 0,
      updatedJobs: json['updated_jobs'] ?? 0,
      progress: json['progress'],
      durationSeconds: (json['duration_seconds'] ?? 0).toDouble(),
      startedAt: json['started_at'] != null ? DateTime.parse(json['started_at']) : null,
      completedAt: json['completed_at'] != null ? DateTime.parse(json['completed_at']) : null,
      createdAt: DateTime.parse(json['created_at']),
    );
  }

  AppException _handleDioError(DioException e) {
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      return NetworkException('Connection timeout');
    } else if (e.type == DioExceptionType.connectionError) {
      return NetworkException('No internet connection');
    }
    final data = e.response?.data;
    final message = (data is Map)
        ? (data['detail'] ?? data['message'] ?? 'Server error')
        : 'Server error';
    return ServerException(message, e.response?.statusCode);
  }
}
