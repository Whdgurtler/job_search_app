import 'package:dartz/dartz.dart';
import '../../core/errors/failures.dart';
import '../entities/user_entity.dart';

abstract class UserRepository {
  Future<Either<Failure, UserEntity>> getUserProfile();

  Future<Either<Failure, UserEntity>> updateUserProfile({
    String? displayName,
    String? phoneNumber,
  });

  Future<Either<Failure, String>> uploadResume(String filePath);

  Future<Either<Failure, void>> deleteResume();
}
