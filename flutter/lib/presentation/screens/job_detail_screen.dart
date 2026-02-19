import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import 'package:url_launcher/url_launcher.dart';
import '../providers/job_provider.dart';

class JobDetailScreen extends ConsumerWidget {
  final String jobId;

  const JobDetailScreen({super.key, required this.jobId});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final jobAsync = ref.watch(jobDetailProvider(jobId));

    return Scaffold(
      appBar: AppBar(
        title: const Text('Job Details'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/jobs'),
        ),
      ),
      body: jobAsync.when(
        data: (job) {
          if (job == null) {
            return const Center(
              child: Text('Job not found'),
            );
          }

          return SingleChildScrollView(
            padding: const EdgeInsets.all(16),
            child: Column(
              crossAxisAlignment: CrossAxisAlignment.start,
              children: [
                Card(
                  child: Padding(
                    padding: const EdgeInsets.all(16),
                    child: Column(
                      crossAxisAlignment: CrossAxisAlignment.start,
                      children: [
                        Text(
                          job.title,
                          style: Theme.of(context).textTheme.headlineSmall,
                        ),
                        const SizedBox(height: 8),
                        Text(
                          job.company,
                          style: Theme.of(context).textTheme.titleMedium?.copyWith(
                                color: Theme.of(context).colorScheme.primary,
                              ),
                        ),
                        const SizedBox(height: 4),
                        Row(
                          children: [
                            const Icon(Icons.location_on, size: 16),
                            const SizedBox(width: 4),
                            Text(job.location),
                          ],
                        ),
                        if (job.displayDate != null) ...[
                          const SizedBox(height: 4),
                          Text(
                            'Posted ${job.displayDate!}',
                            style: Theme.of(context).textTheme.bodySmall,
                          ),
                        ],
                      ],
                    ),
                  ),
                ),
                const SizedBox(height: 16),
                if (job.matchScore > 0)
                  _buildInfoCard(
                    context,
                    'Match Score',
                    '${(job.matchScore * 100).round()}%',
                    Icons.star,
                  ),
                if (job.isRemote)
                  _buildInfoCard(context, 'Remote', 'Yes', Icons.home_work),
                if (job.salary != null)
                  _buildInfoCard(context, 'Salary', job.salary!, Icons.attach_money),
                if (job.employmentType != null)
                  _buildInfoCard(context, 'Employment Type', job.employmentType!, Icons.work),
                if (job.experienceLevel != null)
                  _buildInfoCard(context, 'Experience Level', job.experienceLevel!, Icons.bar_chart),
                if (job.recommendation.isNotEmpty)
                  _buildInfoCard(context, 'Recommendation', job.recommendation, Icons.thumb_up),
                if (job.matchedSkills.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  Text('Matched Skills', style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: job.matchedSkills
                        .map((skill) => Chip(
                              label: Text(skill),
                              backgroundColor: Colors.green.withOpacity(0.1),
                            ))
                        .toList(),
                  ),
                ],
                if (job.missingSkills.isNotEmpty) ...[
                  const SizedBox(height: 16),
                  Text('Skills to Develop', style: Theme.of(context).textTheme.titleMedium),
                  const SizedBox(height: 8),
                  Wrap(
                    spacing: 8,
                    runSpacing: 8,
                    children: job.missingSkills
                        .map((skill) => Chip(
                              label: Text(skill),
                              backgroundColor: Colors.orange.withOpacity(0.1),
                            ))
                        .toList(),
                  ),
                ],
                if (job.description != null) ...[
                  const SizedBox(height: 16),
                  Text(
                    'Description',
                    style: Theme.of(context).textTheme.titleMedium,
                  ),
                  const SizedBox(height: 8),
                  Card(
                    child: Padding(
                      padding: const EdgeInsets.all(16),
                      child: Text(job.description!),
                    ),
                  ),
                ],
                const SizedBox(height: 24),
                if (job.url != null && job.url!.isNotEmpty)
                  SizedBox(
                    width: double.infinity,
                    child: ElevatedButton.icon(
                      onPressed: () async {
                        final uri = Uri.parse(job.url!);
                        if (await canLaunchUrl(uri)) {
                          await launchUrl(uri, mode: LaunchMode.externalApplication);
                        } else {
                          if (context.mounted) {
                            ScaffoldMessenger.of(context).showSnackBar(
                              const SnackBar(content: Text('Could not open URL')),
                            );
                          }
                        }
                      },
                      icon: const Icon(Icons.open_in_new),
                      label: const Text('Apply Now'),
                    ),
                  ),
              ],
            ),
          );
        },
        loading: () => const Center(child: CircularProgressIndicator()),
        error: (error, stack) => Center(
          child: Column(
            mainAxisAlignment: MainAxisAlignment.center,
            children: [
              Text('Error: $error'),
              const SizedBox(height: 16),
              ElevatedButton(
                onPressed: () => ref.refresh(jobDetailProvider(jobId)),
                child: const Text('Retry'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  Widget _buildInfoCard(
    BuildContext context,
    String label,
    String value,
    IconData icon,
  ) {
    return Padding(
      padding: const EdgeInsets.only(bottom: 8),
      child: Card(
        child: ListTile(
          leading: Icon(icon),
          title: Text(label),
          subtitle: Text(value),
        ),
      ),
    );
  }
}
