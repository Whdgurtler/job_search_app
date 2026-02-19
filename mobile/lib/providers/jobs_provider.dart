import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../models/job.dart';
import '../services/api_service.dart';

final apiServiceProvider = Provider<ApiService>((ref) {
  return ApiService();
});

final jobsProvider = FutureProvider<List<Job>>((ref) async {
  final apiService = ref.watch(apiServiceProvider);
  final response = await apiService.getJobs();
  final items = response['items'] as List;
  return items.map((json) => Job.fromJson(json)).toList();
});

final jobProvider = FutureProvider.family<Job, int>((ref, jobId) async {
  final apiService = ref.watch(apiServiceProvider);
  final response = await apiService.getJobById(jobId);
  return Job.fromJson(response);
});
