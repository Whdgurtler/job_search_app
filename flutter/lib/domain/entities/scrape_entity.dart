class ScrapeConfigEntity {
  final String id;
  final String name;
  final String keywords;
  final List<String>? companies;
  final List<String>? employmentAreas;
  final String location;
  final bool isDefault;
  final DateTime createdAt;

  const ScrapeConfigEntity({
    required this.id,
    required this.name,
    required this.keywords,
    this.companies,
    this.employmentAreas,
    required this.location,
    required this.isDefault,
    required this.createdAt,
  });
}

class ScrapeRunEntity {
  final String id;
  final String status;
  final String scrapedDate;
  final List<String>? companies;
  final String keywords;
  final int totalJobs;
  final int newJobs;
  final int updatedJobs;
  final Map<String, dynamic>? progress;
  final double durationSeconds;
  final DateTime? startedAt;
  final DateTime? completedAt;
  final DateTime createdAt;

  const ScrapeRunEntity({
    required this.id,
    required this.status,
    required this.scrapedDate,
    this.companies,
    required this.keywords,
    required this.totalJobs,
    required this.newJobs,
    required this.updatedJobs,
    this.progress,
    required this.durationSeconds,
    this.startedAt,
    this.completedAt,
    required this.createdAt,
  });

  bool get isRunning => status == 'running' || status == 'pending' || status == 'retrying';
  bool get isCompleted => status == 'completed';
  bool get isFailed => status == 'failed';

  double get progressPercent {
    if (progress == null) return 0;
    final completed = progress!['completed_companies'] as int? ?? 0;
    final total = progress!['total_companies'] as int? ?? 1;
    if (total == 0) return 0;
    return completed / total;
  }

  String? get currentCompany => progress?['current_company'] as String?;
}

class ScrapeRunStatusEntity {
  final String id;
  final String status;
  final Map<String, dynamic>? progress;
  final int totalJobs;
  final int newJobs;
  final double durationSeconds;

  const ScrapeRunStatusEntity({
    required this.id,
    required this.status,
    this.progress,
    required this.totalJobs,
    required this.newJobs,
    required this.durationSeconds,
  });

  bool get isRunning => status == 'running' || status == 'pending' || status == 'retrying';
}
