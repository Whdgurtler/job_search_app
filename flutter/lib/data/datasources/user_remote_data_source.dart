import 'package:dio/dio.dart';
import '../../core/constants/app_constants.dart';
import '../../core/errors/exceptions.dart';
import '../../core/network/dio_client.dart';
import '../models/user_model.dart';

abstract class UserRemoteDataSource {
  Future<UserModel> getUserProfile();
  Future<UserModel> updateUserProfile({
    String? displayName,
    String? phoneNumber,
  });
  Future<String> uploadResume(String filePath);
  Future<void> deleteResume();
}

class UserRemoteDataSourceImpl implements UserRemoteDataSource {
  final DioClient _client;

  UserRemoteDataSourceImpl(this._client);

  @override
  Future<UserModel> getUserProfile() async {
    try {
      final response = await _client.get(AppConstants.profileEndpoint);

      if (response.statusCode == 200) {
        return UserModel.fromJson(response.data['data'] ?? response.data);
      } else {
        throw ServerException(
          'Failed to fetch user profile',
          response.statusCode,
        );
      }
    } on DioException catch (e) {
      _handleDioException(e);
      rethrow;
    } catch (e) {
      throw ServerException('Unexpected error: $e');
    }
  }

  @override
  Future<UserModel> updateUserProfile({
    String? displayName,
    String? phoneNumber,
  }) async {
    try {
      final data = <String, dynamic>{
        if (displayName != null) 'display_name': displayName,
        if (phoneNumber != null) 'phone_number': phoneNumber,
      };

      final response = await _client.put(
        AppConstants.profileEndpoint,
        data: data,
      );

      if (response.statusCode == 200) {
        return UserModel.fromJson(response.data['data'] ?? response.data);
      } else {
        throw ServerException(
          'Failed to update profile',
          response.statusCode,
        );
      }
    } on DioException catch (e) {
      _handleDioException(e);
      rethrow;
    } catch (e) {
      throw ServerException('Unexpected error: $e');
    }
  }

  @override
  Future<String> uploadResume(String filePath) async {
    try {
      final response = await _client.uploadFile(
        AppConstants.resumeUploadEndpoint,
        filePath,
        'file',
      );

      if (response.statusCode == 200 || response.statusCode == 201) {
        return response.data['data']['url'] ?? response.data['url'];
      } else {
        throw ServerException(
          'Failed to upload resume',
          response.statusCode,
        );
      }
    } on DioException catch (e) {
      _handleDioException(e);
      rethrow;
    } catch (e) {
      throw ServerException('Unexpected error: $e');
    }
  }

  @override
  Future<void> deleteResume() async {
    try {
      final response = await _client.delete(AppConstants.resumeUploadEndpoint);

      if (response.statusCode != 200 && response.statusCode != 204) {
        throw ServerException(
          'Failed to delete resume',
          response.statusCode,
        );
      }
    } on DioException catch (e) {
      _handleDioException(e);
      rethrow;
    } catch (e) {
      throw ServerException('Unexpected error: $e');
    }
  }

  void _handleDioException(DioException e) {
    if (e.type == DioExceptionType.connectionTimeout ||
        e.type == DioExceptionType.receiveTimeout) {
      throw NetworkException('Connection timeout');
    } else if (e.type == DioExceptionType.connectionError) {
      throw NetworkException('No internet connection');
    } else {
      final data = e.response?.data;
      final message = (data is Map)
          ? (data['detail'] ?? data['message'] ?? 'Server error')
          : 'Server error';
      throw ServerException(message, e.response?.statusCode);
    }
  }
}
