// GENERATED CODE - DO NOT MODIFY BY HAND

part of 'scrape_config.dart';

// **************************************************************************
// JsonSerializableGenerator
// **************************************************************************

_$ScrapeConfigImpl _$$ScrapeConfigImplFromJson(Map<String, dynamic> json) =>
    _$ScrapeConfigImpl(
      id: (json['id'] as num).toInt(),
      userId: (json['userId'] as num).toInt(),
      name: json['name'] as String,
      platform: json['platform'] as String,
      searchParams: json['searchParams'] as Map<String, dynamic>,
      isActive: json['isActive'] as bool,
      schedule: json['schedule'] as String?,
      lastRun:
          json['lastRun'] == null
              ? null
              : DateTime.parse(json['lastRun'] as String),
      createdAt: DateTime.parse(json['createdAt'] as String),
      updatedAt: DateTime.parse(json['updatedAt'] as String),
    );

Map<String, dynamic> _$$ScrapeConfigImplToJson(_$ScrapeConfigImpl instance) =>
    <String, dynamic>{
      'id': instance.id,
      'userId': instance.userId,
      'name': instance.name,
      'platform': instance.platform,
      'searchParams': instance.searchParams,
      'isActive': instance.isActive,
      'schedule': instance.schedule,
      'lastRun': instance.lastRun?.toIso8601String(),
      'createdAt': instance.createdAt.toIso8601String(),
      'updatedAt': instance.updatedAt.toIso8601String(),
    };
