import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../models/job.dart';
import '../providers/jobs_provider.dart';

class JobListScreen extends ConsumerStatefulWidget {
  const JobListScreen({super.key});

  @override
  ConsumerState<JobListScreen> createState() => _JobListScreenState();
}

class _JobListScreenState extends ConsumerState<JobListScreen> {
  final _searchController = TextEditingController();

  @override
  void dispose() {
    _searchController.dispose();
    super.dispose();
  }

  @override
  Widget build(BuildContext context) {
    final jobsAsync = ref.watch(jobsProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Jobs'),
        actions: [
          IconButton(
            icon: const Icon(Icons.settings),
            onPressed: () => context.push('/scrape-configs'),
          ),
          IconButton(
            icon: const Icon(Icons.upload_file),
            onPressed: () => context.push('/resume-upload'),
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.all(16.0),
            child: TextField(
              controller: _searchController,
              decoration: InputDecoration(
                hintText: 'Search jobs...',
                prefixIcon: const Icon(Icons.search),
                border: OutlineInputBorder(
                  borderRadius: BorderRadius.circular(12),
                ),
                suffixIcon: _searchController.text.isNotEmpty
                    ? IconButton(
                        icon: const Icon(Icons.clear),
                        onPressed: () {
                          _searchController.clear();
                          ref.refresh(jobsProvider);
                        },
                      )
                    : null,
              ),
              onSubmitted: (value) {
                ref.refresh(jobsProvider);
              },
            ),
          ),
          Expanded(
            child: jobsAsync.when(
              data: (jobs) {
                if (jobs.isEmpty) {
                  return const Center(
                    child: Column(
                      mainAxisAlignment: MainAxisAlignment.center,
                      children: [
                        Icon(Icons.work_off, size: 64, color: Colors.grey),
                        SizedBox(height: 16),
                        Text('No jobs found'),
                        SizedBox(height: 8),
                        Text(
                          'Configure a scrape to start finding jobs',
                          style: TextStyle(color: Colors.grey),
                        ),
                      ],
                    ),
                  );
                }

                return RefreshIndicator(
                  onRefresh: () async {
                    ref.invalidate(jobsProvider);
                  },
                  child: ListView.builder(
                    itemCount: jobs.length,
                    itemBuilder: (context, index) {
                      final job = jobs[index];
                      return JobCard(job: job);
                    },
                  ),
                );
              },
              loading: () => const Center(child: CircularProgressIndicator()),
              error: (error, stack) => Center(
                child: Column(
                  mainAxisAlignment: MainAxisAlignment.center,
                  children: [
                    const Icon(Icons.error_outline, size: 64, color: Colors.red),
                    const SizedBox(height: 16),
                    Text('Error: $error'),
                    const SizedBox(height: 16),
                    ElevatedButton(
                      onPressed: () => ref.refresh(jobsProvider),
                      child: const Text('Retry'),
                    ),
                  ],
                ),
              ),
            ),
          ),
        ],
      ),
      floatingActionButton: FloatingActionButton(
        onPressed: () => context.push('/scrape-configs'),
        child: const Icon(Icons.add),
      ),
    );
  }
}

class JobCard extends StatelessWidget {
  final Job job;

  const JobCard({super.key, required this.job});

  @override
  Widget build(BuildContext context) {
    return Card(
      margin: const EdgeInsets.symmetric(horizontal: 16, vertical: 8),
      child: InkWell(
        onTap: () => context.push('/jobs/${job.id}'),
        child: Padding(
          padding: const EdgeInsets.all(16.0),
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.start,
            children: [
              Row(
                children: [
                  Expanded(
                    child: Text(
                      job.title,
                      style: Theme.of(context).textTheme.titleMedium?.copyWith(
                            fontWeight: FontWeight.bold,
                          ),
                    ),
                  ),
                  if (job.matchScore != null)
                    Chip(
                      label: Text(
                        '${(job.matchScore! * 100).toStringAsFixed(0)}%',
                        style: const TextStyle(fontWeight: FontWeight.bold),
                      ),
                      backgroundColor: _getMatchScoreColor(job.matchScore!),
                    ),
                ],
              ),
              const SizedBox(height: 8),
              Text(
                job.company,
                style: Theme.of(context).textTheme.bodyLarge,
              ),
              if (job.location != null) ...[
                const SizedBox(height: 4),
                Row(
                  children: [
                    const Icon(Icons.location_on, size: 16, color: Colors.grey),
                    const SizedBox(width: 4),
                    Text(job.location!, style: const TextStyle(color: Colors.grey)),
                  ],
                ),
              ],
              if (job.salary != null) ...[
                const SizedBox(height: 4),
                Row(
                  children: [
                    const Icon(Icons.attach_money, size: 16, color: Colors.grey),
                    const SizedBox(width: 4),
                    Text(job.salary!, style: const TextStyle(color: Colors.grey)),
                  ],
                ),
              ],
              const SizedBox(height: 8),
              Row(
                children: [
                  if (job.jobType != null)
                    Chip(
                      label: Text(job.jobType!),
                      labelStyle: const TextStyle(fontSize: 12),
                    ),
                  if (job.seniority != null) ...[
                    const SizedBox(width: 8),
                    Chip(
                      label: Text(job.seniority!),
                      labelStyle: const TextStyle(fontSize: 12),
                    ),
                  ],
                ],
              ),
            ],
          ),
        ),
      ),
    );
  }

  Color _getMatchScoreColor(double score) {
    if (score >= 0.8) return Colors.green.shade100;
    if (score >= 0.6) return Colors.amber.shade100;
    return Colors.orange.shade100;
  }
}
