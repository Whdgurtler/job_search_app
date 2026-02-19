import 'package:freezed_annotation/freezed_annotation.dart';

part 'job_entity.freezed.dart';
part 'job_entity.g.dart';

@freezed
class JobEntity with _$JobEntity {
  const factory JobEntity({
    required String id,
    required String title,
    required String company,
    required String location,
    String? description,
    String? url,
    @Default(false) bool isRemote,
    @Default(0) double matchScore,
    @Default(0) double skillMatch,
    @Default(0) double levelMatch,
    @Default('') String recommendation,
    @Default('') String levelAssessment,
    @Default([]) List<String> matchedSkills,
    @Default([]) List<String> missingSkills,
    @Default('') String notes,
    String? postingDate,
    String? firstSeen,
    String? lastSeen,
    String? displayDate,
    @Default(false) bool isBookmarked,
    @Default(false) bool isApplied,
    // Legacy fields for backwards compat
    String? salary,
    String? employmentType,
    String? experienceLevel,
    List<String>? skills,
  }) = _JobEntity;

  factory JobEntity.fromJson(Map<String, dynamic> json) =>
      _$JobEntityFromJson(json);
}
