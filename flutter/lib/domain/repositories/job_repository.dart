import 'package:dartz/dartz.dart';
import '../../core/errors/failures.dart';
import '../entities/job_entity.dart';

abstract class JobRepository {
  Future<Either<Failure, List<JobEntity>>> getJobs({
    int page = 1,
    int limit = 20,
    String? search,
    String? location,
  });

  Future<Either<Failure, JobEntity>> getJobById(String id);

  Future<Either<Failure, List<JobEntity>>> searchJobs(String query);
}
