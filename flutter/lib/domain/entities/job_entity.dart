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
    String? salary,
    String? employmentType,
    String? experienceLevel,
    List<String>? skills,
    DateTime? postedDate,
    String? applicationUrl,
  }) = _JobEntity;

  factory JobEntity.fromJson(Map<String, dynamic> json) =>
      _$JobEntityFromJson(json);
}
