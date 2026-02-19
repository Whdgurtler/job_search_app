import 'package:freezed_annotation/freezed_annotation.dart';

part 'resume.freezed.dart';
part 'resume.g.dart';

@freezed
class Resume with _$Resume {
  const factory Resume({
    required int id,
    required int userId,
    required String fileName,
    required String filePath,
    Map<String, dynamic>? parsedData,
    required DateTime uploadedAt,
  }) = _Resume;

  factory Resume.fromJson(Map<String, dynamic> json) => _$ResumeFromJson(json);
}
