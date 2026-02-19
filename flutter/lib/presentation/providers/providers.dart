import 'package:firebase_auth/firebase_auth.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../core/network/dio_client.dart';
import '../../data/datasources/auth_remote_data_source.dart';
import '../../data/datasources/job_remote_data_source.dart';
import '../../data/datasources/scrape_remote_data_source.dart';
import '../../data/datasources/user_remote_data_source.dart';
import '../../data/repositories/auth_repository_impl.dart';
import '../../data/repositories/job_repository_impl.dart';
import '../../data/repositories/scrape_repository_impl.dart';
import '../../data/repositories/user_repository_impl.dart';
import '../../domain/repositories/auth_repository.dart';
import '../../domain/repositories/job_repository.dart';
import '../../domain/repositories/scrape_repository.dart';
import '../../domain/repositories/user_repository.dart';

// Core providers
final sharedPreferencesProvider = Provider<SharedPreferences>((ref) {
  throw UnimplementedError('SharedPreferences must be overridden');
});

final firebaseAuthProvider = Provider<FirebaseAuth>((ref) {
  return FirebaseAuth.instance;
});

final dioClientProvider = Provider<DioClient>((ref) {
  final prefs = ref.watch(sharedPreferencesProvider);
  return DioClient(prefs);
});

// Data source providers
final authRemoteDataSourceProvider = Provider<AuthRemoteDataSource>((ref) {
  final firebaseAuth = ref.watch(firebaseAuthProvider);
  final prefs = ref.watch(sharedPreferencesProvider);
  return AuthRemoteDataSourceImpl(firebaseAuth, prefs);
});

final jobRemoteDataSourceProvider = Provider<JobRemoteDataSource>((ref) {
  final client = ref.watch(dioClientProvider);
  return JobRemoteDataSourceImpl(client);
});

final userRemoteDataSourceProvider = Provider<UserRemoteDataSource>((ref) {
  final client = ref.watch(dioClientProvider);
  return UserRemoteDataSourceImpl(client);
});

final scrapeRemoteDataSourceProvider = Provider<ScrapeRemoteDataSource>((ref) {
  final client = ref.watch(dioClientProvider);
  return ScrapeRemoteDataSourceImpl(client);
});

// Repository providers
final authRepositoryProvider = Provider<AuthRepository>((ref) {
  final dataSource = ref.watch(authRemoteDataSourceProvider);
  return AuthRepositoryImpl(dataSource);
});

final jobRepositoryProvider = Provider<JobRepository>((ref) {
  final dataSource = ref.watch(jobRemoteDataSourceProvider);
  return JobRepositoryImpl(dataSource);
});

final userRepositoryProvider = Provider<UserRepository>((ref) {
  final dataSource = ref.watch(userRemoteDataSourceProvider);
  return UserRepositoryImpl(dataSource);
});

final scrapeRepositoryProvider = Provider<ScrapeRepository>((ref) {
  final dataSource = ref.watch(scrapeRemoteDataSourceProvider);
  return ScrapeRepositoryImpl(dataSource);
});
