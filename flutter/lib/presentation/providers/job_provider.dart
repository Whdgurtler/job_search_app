import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/job_entity.dart';
import '../../domain/repositories/job_repository.dart';
import 'providers.dart';

// Job list state
class JobListState {
  final List<JobEntity> jobs;
  final bool isLoading;
  final String? error;
  final bool hasMore;
  final int currentPage;

  const JobListState({
    this.jobs = const [],
    this.isLoading = false,
    this.error,
    this.hasMore = true,
    this.currentPage = 1,
  });

  JobListState copyWith({
    List<JobEntity>? jobs,
    bool? isLoading,
    String? error,
    bool? hasMore,
    int? currentPage,
  }) {
    return JobListState(
      jobs: jobs ?? this.jobs,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      hasMore: hasMore ?? this.hasMore,
      currentPage: currentPage ?? this.currentPage,
    );
  }
}

// Job list notifier
class JobListNotifier extends StateNotifier<JobListState> {
  final JobRepository _jobRepository;

  JobListNotifier(this._jobRepository) : super(const JobListState()) {
    loadJobs();
  }

  Future<void> loadJobs({String? search, String? location}) async {
    state = state.copyWith(isLoading: true, error: null);
    final result = await _jobRepository.getJobs(
      page: 1,
      search: search,
      location: location,
    );
    result.fold(
      (failure) => state = state.copyWith(isLoading: false, error: failure.message),
      (jobs) => state = state.copyWith(
        jobs: jobs,
        isLoading: false,
        currentPage: 1,
        hasMore: jobs.length >= 20,
      ),
    );
  }

  Future<void> loadMoreJobs({String? search, String? location}) async {
    if (state.isLoading || !state.hasMore) return;

    final nextPage = state.currentPage + 1;
    state = state.copyWith(isLoading: true);
    final result = await _jobRepository.getJobs(
      page: nextPage,
      search: search,
      location: location,
    );
    result.fold(
      (failure) => state = state.copyWith(isLoading: false, error: failure.message),
      (jobs) => state = state.copyWith(
        jobs: [...state.jobs, ...jobs],
        isLoading: false,
        currentPage: nextPage,
        hasMore: jobs.length >= 20,
      ),
    );
  }

  Future<void> searchJobs(String query) async {
    await loadJobs(search: query);
  }

  void refresh() {
    loadJobs();
  }
}

// Job list provider
final jobListProvider = StateNotifierProvider<JobListNotifier, JobListState>((ref) {
  final jobRepository = ref.watch(jobRepositoryProvider);
  return JobListNotifier(jobRepository);
});

// Job detail provider
final jobDetailProvider = FutureProvider.family<JobEntity?, String>((ref, jobId) async {
  final jobRepository = ref.watch(jobRepositoryProvider);
  final result = await jobRepository.getJobById(jobId);
  return result.fold(
    (failure) => null,
    (job) => job,
  );
});
