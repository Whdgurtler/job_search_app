import 'package:dartz/dartz.dart';
import '../../core/errors/exceptions.dart';
import '../../core/errors/failures.dart';
import '../../domain/entities/job_entity.dart';
import '../../domain/repositories/job_repository.dart';
import '../datasources/job_remote_data_source.dart';

class JobRepositoryImpl implements JobRepository {
  final JobRemoteDataSource _remoteDataSource;

  JobRepositoryImpl(this._remoteDataSource);

  @override
  Future<Either<Failure, List<JobEntity>>> getJobs({
    int page = 1,
    int limit = 20,
    String? search,
    String? location,
  }) async {
    try {
      final jobs = await _remoteDataSource.getJobs(
        page: page,
        limit: limit,
        search: search,
        location: location,
      );
      return Right(jobs.map((job) => job.toEntity()).toList());
    } on NetworkException catch (e) {
      return Left(NetworkFailure(e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(e.message));
    } catch (e) {
      return Left(ServerFailure('Unexpected error: $e'));
    }
  }

  @override
  Future<Either<Failure, JobEntity>> getJobById(String id) async {
    try {
      final job = await _remoteDataSource.getJobById(id);
      return Right(job.toEntity());
    } on NetworkException catch (e) {
      return Left(NetworkFailure(e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(e.message));
    } catch (e) {
      return Left(ServerFailure('Unexpected error: $e'));
    }
  }

  @override
  Future<Either<Failure, List<JobEntity>>> searchJobs(String query) async {
    try {
      final jobs = await _remoteDataSource.searchJobs(query);
      return Right(jobs.map((job) => job.toEntity()).toList());
    } on NetworkException catch (e) {
      return Left(NetworkFailure(e.message));
    } on ServerException catch (e) {
      return Left(ServerFailure(e.message));
    } catch (e) {
      return Left(ServerFailure('Unexpected error: $e'));
    }
  }
}
