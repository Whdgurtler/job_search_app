import 'package:flutter_test/flutter_test.dart';
import 'package:job_search_mobile/domain/entities/job_entity.dart';

void main() {
  group('JobEntity Tests', () {
    test('JobEntity should be created with all required fields', () {
      // Arrange & Act
      final job = JobEntity(
        id: '1',
        title: 'Software Engineer',
        company: 'Tech Corp',
        location: 'San Francisco, CA',
        description: 'Build amazing products',
        salary: '\$100k - \$150k',
        employmentType: 'Full-time',
        postedDate: DateTime(2024, 1, 1),
      );

      // Assert
      expect(job.id, '1');
      expect(job.title, 'Software Engineer');
      expect(job.company, 'Tech Corp');
      expect(job.location, 'San Francisco, CA');
      expect(job.employmentType, 'Full-time');
      expect(job.salary, '\$100k - \$150k');
    });

    test('JobEntity should support optional fields', () {
      // Arrange & Act
      final job = JobEntity(
        id: '1',
        title: 'Software Engineer',
        company: 'Tech Corp',
        location: 'San Francisco, CA',
        description: 'Build amazing products',
        salary: '\$100k - \$150k',
        employmentType: 'Full-time',
        postedDate: DateTime(2024, 1, 1),
        experienceLevel: 'Mid-level',
        skills: ['Flutter', 'Dart', 'Firebase'],
        benefits: ['Health Insurance', '401k'],
        remote: true,
      );

      // Assert
      expect(job.experienceLevel, 'Mid-level');
      expect(job.skills, ['Flutter', 'Dart', 'Firebase']);
      expect(job.benefits, ['Health Insurance', '401k']);
      expect(job.remote, true);
    });

    test('JobEntity copyWith should update specified fields', () {
      // Arrange
      final job = JobEntity(
        id: '1',
        title: 'Software Engineer',
        company: 'Tech Corp',
        location: 'San Francisco, CA',
        description: 'Build amazing products',
        salary: '\$100k - \$150k',
        employmentType: 'Full-time',
        postedDate: DateTime(2024, 1, 1),
      );

      // Act
      final updatedJob = job.copyWith(
        title: 'Senior Software Engineer',
        salary: '\$150k - \$200k',
      );

      // Assert
      expect(updatedJob.id, '1'); // Unchanged
      expect(updatedJob.title, 'Senior Software Engineer'); // Changed
      expect(updatedJob.salary, '\$150k - \$200k'); // Changed
      expect(updatedJob.company, 'Tech Corp'); // Unchanged
    });

    test('JobEntity with remote flag', () {
      // Arrange & Act
      final remoteJob = JobEntity(
        id: '1',
        title: 'Remote Developer',
        company: 'Tech Corp',
        location: 'Remote',
        description: 'Work from anywhere',
        salary: '\$100k - \$150k',
        employmentType: 'Full-time',
        postedDate: DateTime(2024, 1, 1),
        remote: true,
      );

      final onsiteJob = JobEntity(
        id: '2',
        title: 'Onsite Developer',
        company: 'Local Corp',
        location: 'New York, NY',
        description: 'Office based',
        salary: '\$100k - \$150k',
        employmentType: 'Full-time',
        postedDate: DateTime(2024, 1, 1),
        remote: false,
      );

      // Assert
      expect(remoteJob.remote, true);
      expect(onsiteJob.remote, false);
    });
  });
}
