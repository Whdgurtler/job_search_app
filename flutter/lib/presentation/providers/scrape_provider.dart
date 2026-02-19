import 'dart:async';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/scrape_entity.dart';
import '../../domain/repositories/scrape_repository.dart';
import 'providers.dart';

// --- Scrape Config State ---

class ScrapeConfigState {
  final List<ScrapeConfigEntity> configs;
  final bool isLoading;
  final String? error;

  const ScrapeConfigState({
    this.configs = const [],
    this.isLoading = false,
    this.error,
  });

  ScrapeConfigState copyWith({
    List<ScrapeConfigEntity>? configs,
    bool? isLoading,
    String? error,
  }) {
    return ScrapeConfigState(
      configs: configs ?? this.configs,
      isLoading: isLoading ?? this.isLoading,
      error: error,
    );
  }
}

class ScrapeConfigNotifier extends StateNotifier<ScrapeConfigState> {
  final ScrapeRepository _repository;

  ScrapeConfigNotifier(this._repository) : super(const ScrapeConfigState()) {
    loadConfigs();
  }

  Future<void> loadConfigs() async {
    state = state.copyWith(isLoading: true, error: null);
    final result = await _repository.getConfigs();
    result.fold(
      (failure) => state = state.copyWith(isLoading: false, error: failure.message),
      (configs) => state = state.copyWith(configs: configs, isLoading: false),
    );
  }

  Future<bool> createConfig({
    required String name,
    required String keywords,
    required List<String> companies,
    List<String>? employmentAreas,
    String? location,
    bool isDefault = false,
  }) async {
    final result = await _repository.createConfig(
      name: name,
      keywords: keywords,
      companies: companies,
      employmentAreas: employmentAreas,
      location: location,
      isDefault: isDefault,
    );
    return result.fold(
      (failure) {
        state = state.copyWith(error: failure.message);
        return false;
      },
      (config) {
        state = state.copyWith(configs: [config, ...state.configs]);
        return true;
      },
    );
  }

  Future<bool> deleteConfig(String configId) async {
    final result = await _repository.deleteConfig(configId);
    return result.fold(
      (failure) {
        state = state.copyWith(error: failure.message);
        return false;
      },
      (_) {
        state = state.copyWith(
          configs: state.configs.where((c) => c.id != configId).toList(),
        );
        return true;
      },
    );
  }
}

// --- Scrape Run State ---

class ScrapeRunState {
  final List<ScrapeRunEntity> runs;
  final bool isLoading;
  final String? error;
  final ScrapeRunEntity? activeRun;

  const ScrapeRunState({
    this.runs = const [],
    this.isLoading = false,
    this.error,
    this.activeRun,
  });

  ScrapeRunState copyWith({
    List<ScrapeRunEntity>? runs,
    bool? isLoading,
    String? error,
    ScrapeRunEntity? activeRun,
    bool clearActiveRun = false,
  }) {
    return ScrapeRunState(
      runs: runs ?? this.runs,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      activeRun: clearActiveRun ? null : (activeRun ?? this.activeRun),
    );
  }
}

class ScrapeRunNotifier extends StateNotifier<ScrapeRunState> {
  final ScrapeRepository _repository;
  Timer? _pollTimer;

  ScrapeRunNotifier(this._repository) : super(const ScrapeRunState()) {
    loadRuns();
  }

  @override
  void dispose() {
    _pollTimer?.cancel();
    super.dispose();
  }

  Future<void> loadRuns() async {
    state = state.copyWith(isLoading: true, error: null);
    final result = await _repository.getRuns();
    result.fold(
      (failure) => state = state.copyWith(isLoading: false, error: failure.message),
      (runs) {
        state = state.copyWith(runs: runs, isLoading: false);
        // Auto-poll if there's an active run
        final active = runs.where((r) => r.isRunning).firstOrNull;
        if (active != null) {
          state = state.copyWith(activeRun: active);
          _startPolling(active.id);
        }
      },
    );
  }

  Future<ScrapeRunEntity?> triggerScrape({
    String? configId,
    List<String>? companies,
    String? keywords,
    List<String>? employmentAreas,
  }) async {
    state = state.copyWith(isLoading: true, error: null);
    final result = await _repository.triggerScrape(
      configId: configId,
      companies: companies,
      keywords: keywords,
      employmentAreas: employmentAreas,
    );
    return result.fold(
      (failure) {
        state = state.copyWith(isLoading: false, error: failure.message);
        return null;
      },
      (run) {
        state = state.copyWith(
          runs: [run, ...state.runs],
          isLoading: false,
          activeRun: run,
        );
        _startPolling(run.id);
        return run;
      },
    );
  }

  void _startPolling(String runId) {
    _pollTimer?.cancel();
    _pollTimer = Timer.periodic(const Duration(seconds: 3), (_) async {
      final result = await _repository.getRunStatus(runId);
      result.fold(
        (_) {},
        (status) {
          if (!status.isRunning) {
            _pollTimer?.cancel();
            loadRuns(); // Refresh full list when done
          } else {
            // Update active run progress
            final updatedRun = ScrapeRunEntity(
              id: status.id,
              status: status.status,
              scrapedDate: state.activeRun?.scrapedDate ?? '',
              companies: state.activeRun?.companies,
              keywords: state.activeRun?.keywords ?? '',
              totalJobs: status.totalJobs,
              newJobs: status.newJobs,
              updatedJobs: state.activeRun?.updatedJobs ?? 0,
              progress: status.progress,
              durationSeconds: status.durationSeconds,
              startedAt: state.activeRun?.startedAt,
              completedAt: null,
              createdAt: state.activeRun?.createdAt ?? DateTime.now(),
            );
            state = state.copyWith(activeRun: updatedRun);
          }
        },
      );
    });
  }
}

// --- Providers ---

final scrapeConfigProvider =
    StateNotifierProvider<ScrapeConfigNotifier, ScrapeConfigState>((ref) {
  final repository = ref.watch(scrapeRepositoryProvider);
  return ScrapeConfigNotifier(repository);
});

final scrapeRunProvider =
    StateNotifierProvider<ScrapeRunNotifier, ScrapeRunState>((ref) {
  final repository = ref.watch(scrapeRepositoryProvider);
  return ScrapeRunNotifier(repository);
});
