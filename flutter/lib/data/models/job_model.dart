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
    String? salary,
    String? employmentType,
    String? experienceLevel,
    List<String>? skills,
    DateTime? postedDate,
    String? applicationUrl,
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
      salary: salary,
      employmentType: employmentType,
      experienceLevel: experienceLevel,
      skills: skills,
      postedDate: postedDate,
      applicationUrl: applicationUrl,
    );
  }

  factory JobModel.fromEntity(JobEntity entity) {
    return JobModel(
      id: entity.id,
      title: entity.title,
      company: entity.company,
      location: entity.location,
      description: entity.description,
      salary: entity.salary,
      employmentType: entity.employmentType,
      experienceLevel: entity.experienceLevel,
      skills: entity.skills,
      postedDate: entity.postedDate,
      applicationUrl: entity.applicationUrl,
    );
  }
}
