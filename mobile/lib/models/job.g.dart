// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'job.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$JobImpl _$$JobImplFromJson(Map<String, dynamic> json) => _$JobImpl(
  id: (json['id'] as num).toInt(),
  userId: (json['userId'] as num).toInt(),
  title: json['title'] as String,
  company: json['company'] as String,
  location: json['location'] as String?,
  description: json['description'] as String?,
  url: json['url'] as String?,
  salary: json['salary'] as String?,
  jobType: json['jobType'] as String?,
  seniority: json['seniority'] as String?,
  source: json['source'] as String,
  sourceJobId: json['sourceJobId'] as String?,
  postedDate:
      json['postedDate'] == null
          ? null
          : DateTime.parse(json['postedDate'] as String),
  scrapedAt: DateTime.parse(json['scrapedAt'] as String),
  matchScore: (json['matchScore'] as num?)?.toDouble(),
  matchReasons: json['matchReasons'] as Map<String, dynamic>?,
  rawData: json['rawData'] as Map<String, dynamic>?,
);

Map<String, dynamic> _$$JobImplToJson(_$JobImpl instance) => <String, dynamic>{
  'id': instance.id,
  'userId': instance.userId,
  'title': instance.title,
  'company': instance.company,
  'location': instance.location,
  'description': instance.description,
  'url': instance.url,
  'salary': instance.salary,
  'jobType': instance.jobType,
  'seniority': instance.seniority,
  'source': instance.source,
  'sourceJobId': instance.sourceJobId,
  'postedDate': instance.postedDate?.toIso8601String(),
  'scrapedAt': instance.scrapedAt.toIso8601String(),
  'matchScore': instance.matchScore,
  'matchReasons': instance.matchReasons,
  'rawData': instance.rawData,
};
