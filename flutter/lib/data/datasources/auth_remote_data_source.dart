import 'package:firebase_auth/firebase_auth.dart';
import 'package:shared_preferences/shared_preferences.dart';
import '../../core/constants/app_constants.dart';
import '../../core/errors/exceptions.dart';
import '../models/user_model.dart';

abstract class AuthRemoteDataSource {
  Future<UserModel> signInWithEmailAndPassword({
    required String email,
    required String password,
  });

  Future<UserModel> signUpWithEmailAndPassword({
    required String email,
    required String password,
    String? displayName,
  });

  Future<void> signOut();

  Future<UserModel?> getCurrentUser();

  Future<bool> isSignedIn();
}

class AuthRemoteDataSourceImpl implements AuthRemoteDataSource {
  final FirebaseAuth _firebaseAuth;
  final SharedPreferences _prefs;

  AuthRemoteDataSourceImpl(this._firebaseAuth, this._prefs);

  @override
  Future<UserModel> signInWithEmailAndPassword({
    required String email,
    required String password,
  }) async {
    try {
      final credential = await _firebaseAuth.signInWithEmailAndPassword(
        email: email,
        password: password,
      );

      if (credential.user == null) {
        throw AuthException('Sign in failed');
      }

      // Get ID token and save it
      final token = await credential.user!.getIdToken();
      await _prefs.setString(AppConstants.tokenKey, token ?? '');
      await _prefs.setString(AppConstants.userIdKey, credential.user!.uid);
      await _prefs.setString(AppConstants.userEmailKey, credential.user!.email ?? '');

      return _userToModel(credential.user!);
    } on FirebaseAuthException catch (e) {
      throw AuthException(_getAuthErrorMessage(e.code));
    } catch (e) {
      throw AuthException('Sign in failed: $e');
    }
  }

  @override
  Future<UserModel> signUpWithEmailAndPassword({
    required String email,
    required String password,
    String? displayName,
  }) async {
    try {
      final credential = await _firebaseAuth.createUserWithEmailAndPassword(
        email: email,
        password: password,
      );

      if (credential.user == null) {
        throw AuthException('Sign up failed');
      }

      // Update display name if provided
      if (displayName != null) {
        await credential.user!.updateDisplayName(displayName);
      }

      // Get ID token and save it
      final token = await credential.user!.getIdToken();
      await _prefs.setString(AppConstants.tokenKey, token ?? '');
      await _prefs.setString(AppConstants.userIdKey, credential.user!.uid);
      await _prefs.setString(AppConstants.userEmailKey, credential.user!.email ?? '');

      return _userToModel(credential.user!);
    } on FirebaseAuthException catch (e) {
      throw AuthException(_getAuthErrorMessage(e.code));
    } catch (e) {
      throw AuthException('Sign up failed: $e');
    }
  }

  @override
  Future<void> signOut() async {
    try {
      await _firebaseAuth.signOut();
      await _prefs.remove(AppConstants.tokenKey);
      await _prefs.remove(AppConstants.userIdKey);
      await _prefs.remove(AppConstants.userEmailKey);
    } catch (e) {
      throw AuthException('Sign out failed: $e');
    }
  }

  @override
  Future<UserModel?> getCurrentUser() async {
    try {
      final user = _firebaseAuth.currentUser;
      if (user == null) return null;

      // Refresh token
      final token = await user.getIdToken(true);
      await _prefs.setString(AppConstants.tokenKey, token ?? '');

      return _userToModel(user);
    } catch (e) {
      return null;
    }
  }

  @override
  Future<bool> isSignedIn() async {
    return _firebaseAuth.currentUser != null;
  }

  UserModel _userToModel(User user) {
    return UserModel(
      id: user.uid,
      email: user.email ?? '',
      displayName: user.displayName,
      photoUrl: user.photoURL,
      phoneNumber: user.phoneNumber,
    );
  }

  String _getAuthErrorMessage(String code) {
    switch (code) {
      case 'user-not-found':
        return 'No user found with this email';
      case 'wrong-password':
        return 'Wrong password';
      case 'email-already-in-use':
        return 'Email already in use';
      case 'invalid-email':
        return 'Invalid email address';
      case 'weak-password':
        return 'Password is too weak';
      case 'user-disabled':
        return 'This user account has been disabled';
      case 'too-many-requests':
        return 'Too many requests. Please try again later';
      case 'operation-not-allowed':
        return 'Operation not allowed';
      default:
        return 'Authentication failed';
    }
  }
}
