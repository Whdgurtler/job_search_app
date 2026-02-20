import 'package:dio/dio.dart';
import '../../core/constants/app_constants.dart';
import '../../core/errors/exceptions.dart';
import '../../core/network/dio_client.dart';
import '../models/job_model.dart';

String _extractErrorMessage(DioException e) {
  final data = e.response?.data;
  if (data is Map) {
    return data['detail'] ?? data['message'] ?? 'Server error';
  }
  return 'Server error';
}

abstract class JobRemoteDataSource {
  Future<List<JobModel>> getJobs({
    int page = 1,
    int limit = 20,
    String? search,
    String? location,
  });

  Future<JobModel> getJobById(String id);

  Future<List<JobModel>> searchJobs(String query);
}

class JobRemoteDataSourceImpl implements JobRemoteDataSource {
  final DioClient _client;

  JobRemoteDataSourceImpl(this._client);

  @override
  Future<List<JobModel>> getJobs({
    int page = 1,
    int limit = 20,
    String? search,
    String? location,
  }) async {
    try {
      final queryParams = <String, dynamic>{
        'page': page,
        'limit': limit,
        if (search != null) 'search': search,
        if (location != null) 'location': location,
      };

      final response = await _client.get(
        AppConstants.jobsEndpoint,
        queryParameters: queryParams,
      );

      if (response.statusCode == 200) {
        final responseData = response.data;
        if (responseData is! Map) return [];
        final List<dynamic> jobs = responseData['jobs'] ?? responseData['data'] ?? [];
        return jobs.map((json) => JobModel.fromJson(json as Map<String, dynamic>)).toList();
      } else {
        throw ServerException(
          'Failed to fetch jobs',
          response.statusCode,
        );
      }
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw NetworkException('Connection timeout');
      } else if (e.type == DioExceptionType.connectionError) {
        throw NetworkException('No internet connection');
      } else {
        throw ServerException(
          _extractErrorMessage(e),
          e.response?.statusCode,
        );
      }
    } on ServerException {
      rethrow;
    } on NetworkException {
      rethrow;
    } catch (e) {
      throw ServerException('Unexpected error: $e');
    }
  }

  @override
  Future<JobModel> getJobById(String id) async {
    try {
      final endpoint = AppConstants.jobDetailsEndpoint.replaceAll('{id}', id);
      final response = await _client.get(endpoint);

      if (response.statusCode == 200) {
        final data = response.data;
        if (data is Map<String, dynamic>) {
          return JobModel.fromJson(data);
        }
        throw ServerException('Invalid response format');
      } else {
        throw ServerException(
          'Failed to fetch job details',
          response.statusCode,
        );
      }
    } on DioException catch (e) {
      if (e.type == DioExceptionType.connectionTimeout ||
          e.type == DioExceptionType.receiveTimeout) {
        throw NetworkException('Connection timeout');
      } else if (e.type == DioExceptionType.connectionError) {
        throw NetworkException('No internet connection');
      } else {
        throw ServerException(
          _extractErrorMessage(e),
          e.response?.statusCode,
        );
      }
    } on ServerException {
      rethrow;
    } on NetworkException {
      rethrow;
    } catch (e) {
      throw ServerException('Unexpected error: $e');
    }
  }

  @override
  Future<List<JobModel>> searchJobs(String query) async {
    return getJobs(search: query);
  }
}
