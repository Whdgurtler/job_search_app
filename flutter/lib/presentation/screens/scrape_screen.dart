import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/scrape_provider.dart';
import '../../domain/entities/scrape_entity.dart';

class ScrapeScreen extends ConsumerWidget {
  const ScrapeScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final configState = ref.watch(scrapeConfigProvider);
    final runState = ref.watch(scrapeRunProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Scrapes'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/jobs'),
        ),
      ),
      body: RefreshIndicator(
        onRefresh: () async {
          ref.read(scrapeConfigProvider.notifier).loadConfigs();
          ref.read(scrapeRunProvider.notifier).loadRuns();
        },
        child: ListView(
          padding: const EdgeInsets.all(16),
          children: [
            // Active Run Progress
            if (runState.activeRun != null && runState.activeRun!.isRunning)
              _ActiveRunCard(run: runState.activeRun!),

            // Configs Section
            Row(
              mainAxisAlignment: MainAxisAlignment.spaceBetween,
              children: [
                Text(
                  'Scrape Configs',
                  style: Theme.of(context).textTheme.titleLarge,
                ),
                IconButton(
                  icon: const Icon(Icons.add),
                  onPressed: () => context.go('/scrapes/new-config'),
                ),
              ],
            ),
            const SizedBox(height: 8),
            if (configState.isLoading)
              const Center(child: CircularProgressIndicator())
            else if (configState.error != null)
              _ErrorCard(
                message: configState.error!,
                onRetry: () => ref.read(scrapeConfigProvider.notifier).loadConfigs(),
              )
            else if (configState.configs.isEmpty)
              Card(
                child: Padding(
                  padding: const EdgeInsets.all(24),
                  child: Column(
                    children: [
                      const Icon(Icons.settings_suggest, size: 48, color: Colors.grey),
                      const SizedBox(height: 8),
                      const Text('No scrape configs yet'),
                      const SizedBox(height: 8),
                      ElevatedButton.icon(
                        onPressed: () => context.go('/scrapes/new-config'),
                        icon: const Icon(Icons.add),
                        label: const Text('Create Config'),
                      ),
                    ],
                  ),
                ),
              )
            else
              ...configState.configs.map((config) => _ConfigCard(config: config)),

            const SizedBox(height: 24),

            // Runs Section
            Text(
              'Recent Runs',
              style: Theme.of(context).textTheme.titleLarge,
            ),
            const SizedBox(height: 8),
            if (runState.isLoading && runState.runs.isEmpty)
              const Center(child: CircularProgressIndicator())
            else if (runState.error != null && runState.runs.isEmpty)
              _ErrorCard(
                message: runState.error!,
                onRetry: () => ref.read(scrapeRunProvider.notifier).loadRuns(),
              )
            else if (runState.runs.isEmpty)
              const Card(
                child: Padding(
                  padding: EdgeInsets.all(24),
                  child: Center(child: Text('No scrape runs yet')),
                ),
              )
            else
              ...runState.runs.map((run) => _RunCard(run: run)),
          ],
        ),
      ),
    );
  }
}

class _ActiveRunCard extends StatelessWidget {
  final ScrapeRunEntity run;

  const _ActiveRunCard({required this.run});

  @override
  Widget build(BuildContext context) {
    return Card(
      color: Theme.of(context).colorScheme.primaryContainer,
      margin: const EdgeInsets.only(bottom: 16),
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          crossAxisAlignment: CrossAxisAlignment.start,
          children: [
            Row(
              children: [
                const SizedBox(
                  width: 20,
                  height: 20,
                  child: CircularProgressIndicator(strokeWidth: 2),
                ),
                const SizedBox(width: 12),
                Text(
                  'Scrape in progress...',
                  style: Theme.of(context).textTheme.titleMedium,
                ),
              ],
            ),
            const SizedBox(height: 12),
            LinearProgressIndicator(value: run.progressPercent),
            const SizedBox(height: 8),
            if (run.currentCompany != null)
              Text('Currently scraping: ${run.currentCompany}'),
            Text(
              '${run.progress?['completed_companies'] ?? 0} / '
              '${run.progress?['total_companies'] ?? '?'} companies '
              '- ${run.progress?['jobs_so_far'] ?? 0} jobs found',
              style: Theme.of(context).textTheme.bodySmall,
            ),
          ],
        ),
      ),
    );
  }
}

class _ConfigCard extends ConsumerWidget {
  final ScrapeConfigEntity config;

  const _ConfigCard({required this.config});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        title: Text(config.name),
        subtitle: Text(
          [
            if (config.companies != null && config.companies!.isNotEmpty)
              '${config.companies!.length} companies',
            if (config.keywords.isNotEmpty) config.keywords,
            if (config.location.isNotEmpty) config.location,
          ].join(' - '),
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        trailing: Row(
          mainAxisSize: MainAxisSize.min,
          children: [
            IconButton(
              icon: const Icon(Icons.play_arrow, color: Colors.green),
              tooltip: 'Run scrape',
              onPressed: () async {
                final run = await ref.read(scrapeRunProvider.notifier).triggerScrape(
                      configId: config.id,
                    );
                if (run != null && context.mounted) {
                  ScaffoldMessenger.of(context).showSnackBar(
                    const SnackBar(content: Text('Scrape started!')),
                  );
                }
              },
            ),
            IconButton(
              icon: const Icon(Icons.delete_outline, color: Colors.red),
              tooltip: 'Delete',
              onPressed: () async {
                final confirmed = await showDialog<bool>(
                  context: context,
                  builder: (ctx) => AlertDialog(
                    title: const Text('Delete Config'),
                    content: Text('Delete "${config.name}"?'),
                    actions: [
                      TextButton(onPressed: () => Navigator.pop(ctx, false), child: const Text('Cancel')),
                      TextButton(onPressed: () => Navigator.pop(ctx, true), child: const Text('Delete')),
                    ],
                  ),
                );
                if (confirmed == true) {
                  ref.read(scrapeConfigProvider.notifier).deleteConfig(config.id);
                }
              },
            ),
          ],
        ),
        leading: config.isDefault
            ? const Icon(Icons.star, color: Colors.amber)
            : const Icon(Icons.settings),
      ),
    );
  }
}

class _RunCard extends StatelessWidget {
  final ScrapeRunEntity run;

  const _RunCard({required this.run});

  @override
  Widget build(BuildContext context) {
    final statusColor = switch (run.status) {
      'completed' => Colors.green,
      'failed' => Colors.red,
      'running' || 'retrying' => Colors.orange,
      _ => Colors.grey,
    };

    final statusIcon = switch (run.status) {
      'completed' => Icons.check_circle,
      'failed' => Icons.error,
      'running' || 'retrying' => Icons.sync,
      _ => Icons.schedule,
    };

    return Card(
      margin: const EdgeInsets.only(bottom: 8),
      child: ListTile(
        leading: Icon(statusIcon, color: statusColor),
        title: Text(
          run.companies?.join(', ') ?? 'Scrape run',
          maxLines: 1,
          overflow: TextOverflow.ellipsis,
        ),
        subtitle: Text(
          '${run.totalJobs} jobs found (${run.newJobs} new) - '
          '${run.durationSeconds.toStringAsFixed(0)}s',
        ),
        trailing: Text(
          run.status,
          style: TextStyle(color: statusColor, fontWeight: FontWeight.bold),
        ),
      ),
    );
  }
}

class _ErrorCard extends StatelessWidget {
  final String message;
  final VoidCallback onRetry;

  const _ErrorCard({required this.message, required this.onRetry});

  @override
  Widget build(BuildContext context) {
    return Card(
      child: Padding(
        padding: const EdgeInsets.all(16),
        child: Column(
          children: [
            Text(message, style: const TextStyle(color: Colors.red)),
            const SizedBox(height: 8),
            ElevatedButton(onPressed: onRetry, child: const Text('Retry')),
          ],
        ),
      ),
    );
  }
}
