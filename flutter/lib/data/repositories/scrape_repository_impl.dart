import 'package:dartz/dartz.dart';
import '../../core/errors/exceptions.dart';
import '../../core/errors/failures.dart';
import '../../domain/entities/scrape_entity.dart';
import '../../domain/repositories/scrape_repository.dart';
import '../datasources/scrape_remote_data_source.dart';

class ScrapeRepositoryImpl implements ScrapeRepository {
  final ScrapeRemoteDataSource _remoteDataSource;

  ScrapeRepositoryImpl(this._remoteDataSource);

  @override
  Future<Either<Failure, List<ScrapeConfigEntity>>> getConfigs() async {
    try {
      final configs = await _remoteDataSource.getConfigs();
      return Right(configs);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(e.message));
    } catch (e) {
      return Left(ServerFailure('Unexpected error: $e'));
    }
  }

  @override
  Future<Either<Failure, ScrapeConfigEntity>> createConfig({
    required String name,
    required String keywords,
    required List<String> companies,
    List<String>? employmentAreas,
    String? location,
    bool isDefault = false,
  }) async {
    try {
      final config = await _remoteDataSource.createConfig({
        'name': name,
        'keywords': keywords,
        'companies': companies,
        'employment_areas': employmentAreas ?? [],
        'location': location ?? '',
        'is_default': isDefault,
      });
      return Right(config);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(e.message));
    } catch (e) {
      return Left(ServerFailure('Unexpected error: $e'));
    }
  }

  @override
  Future<Either<Failure, void>> deleteConfig(String configId) async {
    try {
      await _remoteDataSource.deleteConfig(configId);
      return const Right(null);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(e.message));
    } catch (e) {
      return Left(ServerFailure('Unexpected error: $e'));
    }
  }

  @override
  Future<Either<Failure, ScrapeRunEntity>> triggerScrape({
    String? configId,
    List<String>? companies,
    String? keywords,
    List<String>? employmentAreas,
  }) async {
    try {
      final data = <String, dynamic>{};
      if (configId != null) data['config_id'] = configId;
      if (companies != null) data['companies'] = companies;
      if (keywords != null) data['keywords'] = keywords;
      if (employmentAreas != null) data['employment_areas'] = employmentAreas;
      final run = await _remoteDataSource.triggerScrape(data);
      return Right(run);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(e.message));
    } catch (e) {
      return Left(ServerFailure('Unexpected error: $e'));
    }
  }

  @override
  Future<Either<Failure, List<ScrapeRunEntity>>> getRuns() async {
    try {
      final runs = await _remoteDataSource.getRuns();
      return Right(runs);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(e.message));
    } catch (e) {
      return Left(ServerFailure('Unexpected error: $e'));
    }
  }

  @override
  Future<Either<Failure, ScrapeRunStatusEntity>> getRunStatus(String runId) async {
    try {
      final status = await _remoteDataSource.getRunStatus(runId);
      return Right(status);
    } on NetworkException catch (e) {
      return Left(NetworkFailure(e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(e.message));
    } catch (e) {
      return Left(ServerFailure('Unexpected error: $e'));
    }
  }
}
