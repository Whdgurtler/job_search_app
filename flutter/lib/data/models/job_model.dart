import 'package:freezed_annotation/freezed_annotation.dart';
import '../../domain/entities/job_entity.dart';

part 'job_model.freezed.dart';
part 'job_model.g.dart';

@freezed
class JobModel with _$JobModel {
  const JobModel._();

  const factory JobModel({
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
    // Legacy fields
    String? salary,
    String? employmentType,
    String? experienceLevel,
    List<String>? skills,
  }) = _JobModel;

  factory JobModel.fromJson(Map<String, dynamic> json) =>
      _$JobModelFromJson(json);

  JobEntity toEntity() {
    return JobEntity(
      id: id,
      title: title,
      company: company,
      location: location,
      description: description,
      url: url,
      isRemote: isRemote,
      matchScore: matchScore,
      skillMatch: skillMatch,
      levelMatch: levelMatch,
      recommendation: recommendation,
      levelAssessment: levelAssessment,
      matchedSkills: matchedSkills,
      missingSkills: missingSkills,
      notes: notes,
      postingDate: postingDate,
      firstSeen: firstSeen,
      lastSeen: lastSeen,
      displayDate: displayDate,
      isBookmarked: isBookmarked,
      isApplied: isApplied,
      salary: salary,
      employmentType: employmentType,
      experienceLevel: experienceLevel,
      skills: skills,
    );
  }
}
