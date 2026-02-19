import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/user_entity.dart';
import '../../domain/repositories/user_repository.dart';
import 'providers.dart';

// User profile state
class UserProfileState {
  final UserEntity? user;
  final bool isLoading;
  final String? error;
  final bool isUploading;
  final String? uploadError;

  const UserProfileState({
    this.user,
    this.isLoading = false,
    this.error,
    this.isUploading = false,
    this.uploadError,
  });

  UserProfileState copyWith({
    UserEntity? user,
    bool? isLoading,
    String? error,
    bool? isUploading,
    String? uploadError,
  }) {
    return UserProfileState(
      user: user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      isUploading: isUploading ?? this.isUploading,
      uploadError: uploadError,
    );
  }
}

// User profile notifier
class UserProfileNotifier extends StateNotifier<UserProfileState> {
  final UserRepository _userRepository;

  UserProfileNotifier(this._userRepository) : super(const UserProfileState()) {
    loadProfile();
  }

  Future<void> loadProfile() async {
    state = state.copyWith(isLoading: true, error: null);
    final result = await _userRepository.getUserProfile();
    result.fold(
      (failure) => state = state.copyWith(isLoading: false, error: failure.message),
      (user) => state = state.copyWith(user: user, isLoading: false),
    );
  }

  Future<void> updateProfile({String? displayName, String? phoneNumber}) async {
    state = state.copyWith(isLoading: true, error: null);
    final result = await _userRepository.updateUserProfile(
      displayName: displayName,
      phoneNumber: phoneNumber,
    );
    result.fold(
      (failure) => state = state.copyWith(isLoading: false, error: failure.message),
      (user) => state = state.copyWith(user: user, isLoading: false),
    );
  }

  Future<void> uploadResume(String filePath) async {
    state = state.copyWith(isUploading: true, uploadError: null);
    final result = await _userRepository.uploadResume(filePath);
    result.fold(
      (failure) => state = state.copyWith(isUploading: false, uploadError: failure.message),
      (url) {
        state = state.copyWith(
          isUploading: false,
          user: state.user?.copyWith(resumeUrl: url),
        );
      },
    );
  }

  Future<void> deleteResume() async {
    state = state.copyWith(isUploading: true, uploadError: null);
    final result = await _userRepository.deleteResume();
    result.fold(
      (failure) => state = state.copyWith(isUploading: false, uploadError: failure.message),
      (_) {
        state = state.copyWith(
          isUploading: false,
          user: state.user?.copyWith(resumeUrl: null),
        );
      },
    );
  }
}

// User profile provider
final userProfileProvider = StateNotifierProvider<UserProfileNotifier, UserProfileState>((ref) {
  final userRepository = ref.watch(userRepositoryProvider);
  return UserProfileNotifier(userRepository);
});
