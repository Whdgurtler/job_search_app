import 'package:dio/dio.dart';
import 'package:firebase_auth/firebase_auth.dart';

class ApiService {
  late final Dio _dio;
  final FirebaseAuth _auth;
  
  // Backend API base URL - adjust for your environment
  static const String baseUrl = 'http://localhost:8000/api/v1';
  
  ApiService({FirebaseAuth? auth}) : _auth = auth ?? FirebaseAuth.instance {
    _dio = Dio(BaseOptions(
      baseUrl: baseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
      headers: {
        'Content-Type': 'application/json',
      },
    ));
    
    // Add interceptor to attach Firebase ID token to requests
    _dio.interceptors.add(InterceptorsWrapper(
      onRequest: (options, handler) async {
        final user = _auth.currentUser;
        if (user != null) {
          final token = await user.getIdToken();
          options.headers['Authorization'] = 'Bearer $token';
        }
        return handler.next(options);
      },
      onError: (error, handler) {
        // Handle 401 errors - potentially refresh token or logout
        if (error.response?.statusCode == 401) {
          // Token expired or invalid
          _auth.signOut();
        }
        return handler.next(error);
      },
    ));
  }
  
  // User endpoints
  Future<Map<String, dynamic>> getCurrentUser() async {
    final response = await _dio.get('/users/me');
    return response.data;
  }
  
  Future<Map<String, dynamic>> updateUser(Map<String, dynamic> data) async {
    final response = await _dio.put('/users/me', data: data);
    return response.data;
  }
  
  // Resume endpoints
  Future<List<dynamic>> getResumes() async {
    final response = await _dio.get('/resumes');
    return response.data;
  }
  
  Future<Map<String, dynamic>> uploadResume(String filePath, String fileName) async {
    final formData = FormData.fromMap({
      'file': await MultipartFile.fromFile(filePath, filename: fileName),
    });
    final response = await _dio.post('/resumes/upload', data: formData);
    return response.data;
  }
  
  Future<void> deleteResume(int resumeId) async {
    await _dio.delete('/resumes/$resumeId');
  }
  
  // Job endpoints
  Future<Map<String, dynamic>> getJobs({
    int? page = 1,
    int? pageSize = 20,
    String? sortBy,
    String? search,
  }) async {
    final response = await _dio.get('/jobs', queryParameters: {
      'page': page,
      'page_size': pageSize,
      if (sortBy != null) 'sort_by': sortBy,
      if (search != null) 'search': search,
    });
    return response.data;
  }
  
  Future<Map<String, dynamic>> getJobById(int jobId) async {
    final response = await _dio.get('/jobs/$jobId');
    return response.data;
  }
  
  // Scrape config endpoints
  Future<List<dynamic>> getScrapeConfigs() async {
    final response = await _dio.get('/scrape-configs');
    return response.data;
  }
  
  Future<Map<String, dynamic>> createScrapeConfig(Map<String, dynamic> config) async {
    final response = await _dio.post('/scrape-configs', data: config);
    return response.data;
  }
  
  Future<Map<String, dynamic>> updateScrapeConfig(int configId, Map<String, dynamic> config) async {
    final response = await _dio.put('/scrape-configs/$configId', data: config);
    return response.data;
  }
  
  Future<void> deleteScrapeConfig(int configId) async {
    await _dio.delete('/scrape-configs/$configId');
  }
  
  Future<Map<String, dynamic>> triggerScrape(int configId) async {
    final response = await _dio.post('/scrape-configs/$configId/trigger');
    return response.data;
  }
  
  // Scrape run endpoints
  Future<List<dynamic>> getScrapeRuns({int? page = 1, int? pageSize = 20}) async {
    final response = await _dio.get('/scrape-runs', queryParameters: {
      'page': page,
      'page_size': pageSize,
    });
    return response.data;
  }
  
  Future<Map<String, dynamic>> getScrapeRunById(int runId) async {
    final response = await _dio.get('/scrape-runs/$runId');
    return response.data;
  }
}
