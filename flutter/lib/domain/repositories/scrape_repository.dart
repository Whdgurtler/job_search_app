import 'package:dartz/dartz.dart';
import '../../core/errors/failures.dart';
import '../entities/scrape_entity.dart';

abstract class ScrapeRepository {
  Future<Either<Failure, List<ScrapeConfigEntity>>> getConfigs();
  Future<Either<Failure, ScrapeConfigEntity>> createConfig({
    required String name,
    required String keywords,
    required List<String> companies,
    List<String>? employmentAreas,
    String? location,
    bool isDefault = false,
  });
  Future<Either<Failure, void>> deleteConfig(String configId);
  Future<Either<Failure, ScrapeRunEntity>> triggerScrape({
    String? configId,
    List<String>? companies,
    String? keywords,
    List<String>? employmentAreas,
  });
  Future<Either<Failure, List<ScrapeRunEntity>>> getRuns();
  Future<Either<Failure, ScrapeRunStatusEntity>> getRunStatus(String runId);
}
