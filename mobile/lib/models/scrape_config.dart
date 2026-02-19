import 'package:freezed_annotation/freezed_annotation.dart';

part 'scrape_config.freezed.dart';
part 'scrape_config.g.dart';

@freezed
class ScrapeConfig with _$ScrapeConfig {
  const factory ScrapeConfig({
    required int id,
    required int userId,
    required String name,
    required String platform,
    required Map<String, dynamic> searchParams,
    required bool isActive,
    String? schedule,
    DateTime? lastRun,
    required DateTime createdAt,
    required DateTime updatedAt,
  }) = _ScrapeConfig;

  factory ScrapeConfig.fromJson(Map<String, dynamic> json) => _$ScrapeConfigFromJson(json);
}
