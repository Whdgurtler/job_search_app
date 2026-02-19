import 'package:freezed_annotation/freezed_annotation.dart';

part 'job.freezed.dart';
part 'job.g.dart';

@freezed
class Job with _$Job {
  const factory Job({
    required int id,
    required int userId,
    required String title,
    required String company,
    String? location,
    String? description,
    String? url,
    String? salary,
    String? jobType,
    String? seniority,
    required String source,
    String? sourceJobId,
    DateTime? postedDate,
    required DateTime scrapedAt,
    double? matchScore,
    Map<String, dynamic>? matchReasons,
    Map<String, dynamic>? rawData,
  }) = _Job;

  factory Job.fromJson(Map<String, dynamic> json) => _$JobFromJson(json);
}
