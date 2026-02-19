import 'package:flutter_riverpod/flutter_riverpod.dart';
import '../../domain/entities/user_entity.dart';
import '../../domain/repositories/auth_repository.dart';
import 'providers.dart';

// Auth state
class AuthState {
  final UserEntity? user;
  final bool isLoading;
  final String? error;
  final bool isAuthenticated;

  const AuthState({
    this.user,
    this.isLoading = false,
    this.error,
    this.isAuthenticated = false,
  });

  AuthState copyWith({
    UserEntity? user,
    bool? isLoading,
    String? error,
    bool? isAuthenticated,
  }) {
    return AuthState(
      user: user ?? this.user,
      isLoading: isLoading ?? this.isLoading,
      error: error,
      isAuthenticated: isAuthenticated ?? this.isAuthenticated,
    );
  }
}

// Auth notifier
class AuthNotifier extends StateNotifier<AuthState> {
  final AuthRepository _authRepository;

  AuthNotifier(this._authRepository) : super(const AuthState()) {
    _checkAuthStatus();
  }

  Future<void> _checkAuthStatus() async {
    state = state.copyWith(isLoading: true);
    final result = await _authRepository.isSignedIn();
    result.fold(
      (failure) => state = state.copyWith(isLoading: false, error: failure.message),
      (isSignedIn) async {
        if (isSignedIn) {
          final userResult = await _authRepository.getCurrentUser();
          userResult.fold(
            (failure) => state = state.copyWith(isLoading: false, error: failure.message),
            (user) => state = state.copyWith(
              user: user,
              isLoading: false,
              isAuthenticated: user != null,
            ),
          );
        } else {
          state = state.copyWith(isLoading: false);
        }
      },
    );
  }

  Future<void> signIn(String email, String password) async {
    state = state.copyWith(isLoading: true, error: null);
    final result = await _authRepository.signInWithEmailAndPassword(
      email: email,
      password: password,
    );
    result.fold(
      (failure) => state = state.copyWith(isLoading: false, error: failure.message),
      (user) => state = state.copyWith(
        user: user,
        isLoading: false,
        isAuthenticated: true,
        error: null,
      ),
    );
  }

  Future<void> signUp(String email, String password, String? displayName) async {
    state = state.copyWith(isLoading: true, error: null);
    final result = await _authRepository.signUpWithEmailAndPassword(
      email: email,
      password: password,
      displayName: displayName,
    );
    result.fold(
      (failure) => state = state.copyWith(isLoading: false, error: failure.message),
      (user) => state = state.copyWith(
        user: user,
        isLoading: false,
        isAuthenticated: true,
        error: null,
      ),
    );
  }

  Future<void> signOut() async {
    state = state.copyWith(isLoading: true);
    final result = await _authRepository.signOut();
    result.fold(
      (failure) => state = state.copyWith(isLoading: false, error: failure.message),
      (_) => state = const AuthState(),
    );
  }
}

// Auth provider
final authProvider = StateNotifierProvider<AuthNotifier, AuthState>((ref) {
  final authRepository = ref.watch(authRepositoryProvider);
  return AuthNotifier(authRepository);
});
