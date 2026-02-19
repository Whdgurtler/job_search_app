import 'package:flutter_test/flutter_test.dart';
import 'package:job_search_mobile/domain/entities/user_entity.dart';

void main() {
  group('UserEntity Tests', () {
    test('UserEntity should be created with all required fields', () {
      // Arrange & Act
      const user = UserEntity(
        id: '123',
        email: 'test@example.com',
        name: 'Test User',
        phoneNumber: '+1234567890',
      );

      // Assert
      expect(user.id, '123');
      expect(user.email, 'test@example.com');
      expect(user.name, 'Test User');
      expect(user.phoneNumber, '+1234567890');
      expect(user.profilePictureUrl, null);
      expect(user.resumeUrl, null);
    });

    test('UserEntity should support optional fields', () {
      // Arrange & Act
      const user = UserEntity(
        id: '123',
        email: 'test@example.com',
        name: 'Test User',
        phoneNumber: '+1234567890',
        profilePictureUrl: 'https://example.com/pic.jpg',
        resumeUrl: 'https://example.com/resume.pdf',
      );

      // Assert
      expect(user.profilePictureUrl, 'https://example.com/pic.jpg');
      expect(user.resumeUrl, 'https://example.com/resume.pdf');
    });

    test('UserEntity copyWith should update specified fields', () {
      // Arrange
      const user = UserEntity(
        id: '123',
        email: 'test@example.com',
        name: 'Test User',
        phoneNumber: '+1234567890',
      );

      // Act
      final updatedUser = user.copyWith(
        name: 'Updated Name',
        profilePictureUrl: 'https://example.com/new-pic.jpg',
      );

      // Assert
      expect(updatedUser.id, '123'); // Unchanged
      expect(updatedUser.email, 'test@example.com'); // Unchanged
      expect(updatedUser.name, 'Updated Name'); // Changed
      expect(updatedUser.phoneNumber, '+1234567890'); // Unchanged
      expect(updatedUser.profilePictureUrl, 'https://example.com/new-pic.jpg'); // Changed
    });

    test('UserEntity equality should work correctly', () {
      // Arrange
      const user1 = UserEntity(
        id: '123',
        email: 'test@example.com',
        name: 'Test User',
        phoneNumber: '+1234567890',
      );

      const user2 = UserEntity(
        id: '123',
        email: 'test@example.com',
        name: 'Test User',
        phoneNumber: '+1234567890',
      );

      const user3 = UserEntity(
        id: '456',
        email: 'other@example.com',
        name: 'Other User',
        phoneNumber: '+0987654321',
      );

      // Assert
      expect(user1, equals(user2));
      expect(user1, isNot(equals(user3)));
    });
  });
}
