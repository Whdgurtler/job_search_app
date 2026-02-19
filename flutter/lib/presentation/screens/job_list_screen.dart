import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/job_provider.dart';
import '../widgets/job_card.dart';

class JobListScreen extends ConsumerStatefulWidget {
  const JobListScreen({super.key});

  @override
  ConsumerState<JobListScreen> createState() => _JobListScreenState();
}

class _JobListScreenState extends ConsumerState<JobListScreen> {
  final _scrollController = ScrollController();
  final _searchController = TextEditingController();
  String? _selectedLocation;
  String? _selectedType;

  static const _locations = ['Remote', 'New York', 'San Francisco', 'Los Angeles', 'Chicago', 'Austin', 'Seattle'];
  static const _employmentTypes = ['Full-time', 'Part-time', 'Contract', 'Internship'];

  @override
  void initState() {
    super.initState();
    _scrollController.addListener(_onScroll);
  }

  @override
  void dispose() {
    _scrollController.dispose();
    _searchController.dispose();
    super.dispose();
  }

  void _onScroll() {
    if (_scrollController.position.pixels >=
        _scrollController.position.maxScrollExtent * 0.9) {
      ref.read(jobListProvider.notifier).loadMoreJobs(
            search: _searchController.text.isEmpty ? null : _searchController.text,
            location: _selectedLocation,
          );
    }
  }

  void _applyFilters() {
    ref.read(jobListProvider.notifier).loadJobs(
          search: _searchController.text.isEmpty ? null : _searchController.text,
          location: _selectedLocation,
        );
  }

  void _clearFilters() {
    setState(() {
      _searchController.clear();
      _selectedLocation = null;
      _selectedType = null;
    });
    ref.read(jobListProvider.notifier).refresh();
  }

  bool get _hasActiveFilters =>
      _searchController.text.isNotEmpty ||
      _selectedLocation != null ||
      _selectedType != null;

  void _showFilterSheet() {
    showModalBottomSheet(
      context: context,
      isScrollControlled: true,
      builder: (ctx) => StatefulBuilder(
        builder: (ctx, setSheetState) => Padding(
          padding: EdgeInsets.only(
            left: 16,
            right: 16,
            top: 16,
            bottom: MediaQuery.of(ctx).viewInsets.bottom + 16,
          ),
          child: Column(
            mainAxisSize: MainAxisSize.min,
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              Row(
                mainAxisAlignment: MainAxisAlignment.spaceBetween,
                children: [
                  Text('Filters', style: Theme.of(ctx).textTheme.titleLarge),
                  TextButton(
                    onPressed: () {
                      setSheetState(() {
                        _selectedLocation = null;
                        _selectedType = null;
                      });
                      setState(() {});
                    },
                    child: const Text('Clear'),
                  ),
                ],
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: _selectedLocation,
                decoration: const InputDecoration(
                  labelText: 'Location',
                  prefixIcon: Icon(Icons.location_on),
                ),
                items: [
                  const DropdownMenuItem(value: null, child: Text('All Locations')),
                  ..._locations.map((l) => DropdownMenuItem(value: l, child: Text(l))),
                ],
                onChanged: (v) {
                  setSheetState(() => _selectedLocation = v);
                  setState(() {});
                },
              ),
              const SizedBox(height: 16),
              DropdownButtonFormField<String>(
                value: _selectedType,
                decoration: const InputDecoration(
                  labelText: 'Employment Type',
                  prefixIcon: Icon(Icons.work),
                ),
                items: [
                  const DropdownMenuItem(value: null, child: Text('All Types')),
                  ..._employmentTypes.map((t) => DropdownMenuItem(value: t, child: Text(t))),
                ],
                onChanged: (v) {
                  setSheetState(() => _selectedType = v);
                  setState(() {});
                },
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: () {
                  Navigator.pop(ctx);
                  _applyFilters();
                },
                child: const Text('Apply Filters'),
              ),
            ],
          ),
        ),
      ),
    );
  }

  @override
  Widget build(BuildContext context) {
    final jobState = ref.watch(jobListProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Job Search'),
        actions: [
          IconButton(
            icon: const Icon(Icons.radar),
            tooltip: 'Scrapes',
            onPressed: () => context.go('/scrapes'),
          ),
          IconButton(
            icon: const Icon(Icons.person),
            onPressed: () => context.go('/profile'),
          ),
        ],
      ),
      body: Column(
        children: [
          Padding(
            padding: const EdgeInsets.fromLTRB(16, 16, 16, 8),
            child: Row(
              children: [
                Expanded(
                  child: TextField(
                    controller: _searchController,
                    decoration: InputDecoration(
                      hintText: 'Search jobs...',
                      prefixIcon: const Icon(Icons.search),
                      suffixIcon: _searchController.text.isNotEmpty
                          ? IconButton(
                              icon: const Icon(Icons.clear),
                              onPressed: () {
                                _searchController.clear();
                                _applyFilters();
                              },
                            )
                          : null,
                    ),
                    onSubmitted: (_) => _applyFilters(),
                  ),
                ),
                const SizedBox(width: 8),
                Badge(
                  isLabelVisible: _hasActiveFilters,
                  child: IconButton(
                    icon: const Icon(Icons.tune),
                    tooltip: 'Filters',
                    onPressed: _showFilterSheet,
                  ),
                ),
              ],
            ),
          ),
          if (_hasActiveFilters)
            Padding(
              padding: const EdgeInsets.symmetric(horizontal: 16),
              child: Row(
                children: [
                  if (_selectedLocation != null)
                    Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: Chip(
                        label: Text(_selectedLocation!),
                        onDeleted: () {
                          setState(() => _selectedLocation = null);
                          _applyFilters();
                        },
                      ),
                    ),
                  if (_selectedType != null)
                    Padding(
                      padding: const EdgeInsets.only(right: 8),
                      child: Chip(
                        label: Text(_selectedType!),
                        onDeleted: () {
                          setState(() => _selectedType = null);
                          _applyFilters();
                        },
                      ),
                    ),
                  const Spacer(),
                  TextButton(
                    onPressed: _clearFilters,
                    child: const Text('Clear all'),
                  ),
                ],
              ),
            ),
          Expanded(
            child: jobState.isLoading && jobState.jobs.isEmpty
                ? const Center(child: CircularProgressIndicator())
                : jobState.error != null && jobState.jobs.isEmpty
                    ? Center(
                        child: Column(
                          mainAxisAlignment: MainAxisAlignment.center,
                          children: [
                            Text(jobState.error!),
                            const SizedBox(height: 16),
                            ElevatedButton(
                              onPressed: () =>
                                  ref.read(jobListProvider.notifier).refresh(),
                              child: const Text('Retry'),
                            ),
                          ],
                        ),
                      )
                    : RefreshIndicator(
                        onRefresh: () async {
                          ref.read(jobListProvider.notifier).refresh();
                        },
                        child: jobState.jobs.isEmpty
                            ? ListView(
                                children: const [
                                  SizedBox(height: 100),
                                  Center(
                                    child: Column(
                                      children: [
                                        Icon(Icons.work_off, size: 64, color: Colors.grey),
                                        SizedBox(height: 16),
                                        Text('No jobs found'),
                                        SizedBox(height: 8),
                                        Text(
                                          'Try adjusting your search or filters',
                                          style: TextStyle(color: Colors.grey),
                                        ),
                                      ],
                                    ),
                                  ),
                                ],
                              )
                            : ListView.builder(
                                controller: _scrollController,
                                padding: const EdgeInsets.all(16),
                                itemCount: jobState.jobs.length +
                                    (jobState.isLoading ? 1 : 0),
                                itemBuilder: (context, index) {
                                  if (index == jobState.jobs.length) {
                                    return const Center(
                                      child: Padding(
                                        padding: EdgeInsets.all(16.0),
                                        child: CircularProgressIndicator(),
                                      ),
                                    );
                                  }
                                  final job = jobState.jobs[index];
                                  return JobCard(
                                    job: job,
                                    onTap: () => context.go('/job/${job.id}'),
                                  );
                                },
                              ),
                      ),
          ),
        ],
      ),
    );
  }
}
