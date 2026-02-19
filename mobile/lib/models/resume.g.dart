// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'resume.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$ResumeImpl _$$ResumeImplFromJson(Map<String, dynamic> json) => _$ResumeImpl(
  id: (json['id'] as num).toInt(),
  userId: (json['userId'] as num).toInt(),
  fileName: json['fileName'] as String,
  filePath: json['filePath'] as String,
  parsedData: json['parsedData'] as Map<String, dynamic>?,
  uploadedAt: DateTime.parse(json['uploadedAt'] as String),
);

Map<String, dynamic> _$$ResumeImplToJson(_$ResumeImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'userId': instance.userId,
      'fileName': instance.fileName,
      'filePath': instance.filePath,
      'parsedData': instance.parsedData,
      'uploadedAt': instance.uploadedAt.toIso8601String(),
    };
