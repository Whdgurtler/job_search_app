import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../../data/datasources/scrape_remote_data_source.dart';
import '../providers/scrape_provider.dart';

const _defaultSectors = [
  'Technology',
  'Finance & Banking',
  'Healthcare',
  'Manufacturing',
  'Retail & E-Commerce',
  'Energy',
  'Consulting',
  'Insurance',
  'Government',
  'Education',
  'Media & Entertainment',
  'Real Estate',
  'Telecommunications',
  'Transportation & Logistics',
  'Aerospace & Defense',
];

class ScrapeConfigFormScreen extends ConsumerStatefulWidget {
  const ScrapeConfigFormScreen({super.key});

  @override
  ConsumerState<ScrapeConfigFormScreen> createState() => _ScrapeConfigFormScreenState();
}

class _ScrapeConfigFormScreenState extends ConsumerState<ScrapeConfigFormScreen> {
  final _formKey = GlobalKey<FormState>();
  final _nameController = TextEditingController(text: 'My Config');
  final _keywordsController = TextEditingController();
  final _locationController = TextEditingController();
  final _companyController = TextEditingController();
  final List<String> _companies = [];
  final Set<String> _selectedSuggestions = {};
  final Set<String> _selectedSectors = {};
  bool _isDefault = false;
  bool _isSubmitting = false;

  @override
  void dispose() {
    _nameController.dispose();
    _keywordsController.dispose();
    _locationController.dispose();
    _companyController.dispose();
    super.dispose();
  }

  void _addCompany() {
    final company = _companyController.text.trim();
    if (company.isNotEmpty && !_companies.contains(company)) {
      setState(() {
        _companies.add(company);
        _companyController.clear();
      });
    }
  }

  void _toggleSuggestion(CompanySuggestion suggestion) {
    setState(() {
      if (_selectedSuggestions.contains(suggestion.name)) {
        _selectedSuggestions.remove(suggestion.name);
        _companies.remove(suggestion.name);
      } else {
        _selectedSuggestions.add(suggestion.name);
        if (!_companies.contains(suggestion.name)) {
          _companies.add(suggestion.name);
        }
      }
    });
  }

  void _toggleSector(String sector) {
    setState(() {
      if (_selectedSectors.contains(sector)) {
        _selectedSectors.remove(sector);
      } else {
        _selectedSectors.add(sector);
      }
    });
  }

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_companies.isEmpty && _selectedSectors.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Add at least one company or select a sector')),
      );
      return;
    }

    setState(() => _isSubmitting = true);

    final success = await ref.read(scrapeConfigProvider.notifier).createConfig(
          name: _nameController.text.trim(),
          keywords: _keywordsController.text.trim(),
          companies: _companies,
          employmentAreas: _selectedSectors.isNotEmpty
              ? _selectedSectors.toList()
              : null,
          location: _locationController.text.trim().isEmpty
              ? null
              : _locationController.text.trim(),
          isDefault: _isDefault,
        );

    setState(() => _isSubmitting = false);

    if (success && mounted) {
      context.go('/scrapes');
    } else if (mounted) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Failed to create config')),
      );
    }
  }

  @override
  Widget build(BuildContext context) {
    final suggestionsAsync = ref.watch(companySuggestionsProvider);
    final theme = Theme.of(context);

    return Scaffold(
      appBar: AppBar(
        title: const Text('New Scrape Config'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/scrapes'),
        ),
      ),
      body: SingleChildScrollView(
        padding: const EdgeInsets.all(16),
        child: Form(
          key: _formKey,
          child: Column(
            crossAxisAlignment: CrossAxisAlignment.stretch,
            children: [
              TextFormField(
                controller: _nameController,
                decoration: const InputDecoration(
                  labelText: 'Config Name',
                  hintText: 'e.g. Tech Jobs SF',
                ),
                validator: (v) => v == null || v.trim().isEmpty ? 'Required' : null,
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _keywordsController,
                decoration: const InputDecoration(
                  labelText: 'Keywords',
                  hintText: 'e.g. software engineer, backend, python',
                ),
              ),
              const SizedBox(height: 16),
              TextFormField(
                controller: _locationController,
                decoration: const InputDecoration(
                  labelText: 'Location (optional)',
                  hintText: 'e.g. San Francisco, CA',
                ),
              ),

              // --- Sectors / Employment Areas ---
              const SizedBox(height: 24),
              Text('Sectors', style: theme.textTheme.titleMedium),
              const SizedBox(height: 4),
              Text(
                'Select sectors to auto-discover 10-20 companies per sector',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 4,
                children: _defaultSectors.map((sector) {
                  final selected = _selectedSectors.contains(sector);
                  return FilterChip(
                    label: Text(sector),
                    selected: selected,
                    onSelected: (_) => _toggleSector(sector),
                  );
                }).toList(),
              ),

              // --- Suggested Companies ---
              const SizedBox(height: 24),
              Text('Suggested Companies', style: theme.textTheme.titleMedium),
              const SizedBox(height: 4),
              Text(
                'Based on your resume — tap to add',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 8),
              suggestionsAsync.when(
                loading: () => const Padding(
                  padding: EdgeInsets.symmetric(vertical: 12),
                  child: Center(
                    child: Row(
                      mainAxisSize: MainAxisSize.min,
                      children: [
                        SizedBox(
                          height: 16,
                          width: 16,
                          child: CircularProgressIndicator(strokeWidth: 2),
                        ),
                        SizedBox(width: 8),
                        Text('Loading suggestions...'),
                      ],
                    ),
                  ),
                ),
                error: (_, __) => Text(
                  'Could not load suggestions. Upload a resume first.',
                  style: theme.textTheme.bodySmall?.copyWith(
                    color: theme.colorScheme.onSurfaceVariant,
                  ),
                ),
                data: (suggestions) {
                  if (suggestions.isEmpty) {
                    return Text(
                      'No suggestions available. Upload a resume to get personalized company suggestions.',
                      style: theme.textTheme.bodySmall?.copyWith(
                        color: theme.colorScheme.onSurfaceVariant,
                      ),
                    );
                  }
                  return Wrap(
                    spacing: 8,
                    runSpacing: 4,
                    children: suggestions.map((s) {
                      final selected = _selectedSuggestions.contains(s.name);
                      return Tooltip(
                        message: s.reason,
                        child: FilterChip(
                          label: Text(s.name),
                          selected: selected,
                          onSelected: (_) => _toggleSuggestion(s),
                        ),
                      );
                    }).toList(),
                  );
                },
              ),

              // --- Manual Companies ---
              const SizedBox(height: 24),
              Text('Companies', style: theme.textTheme.titleMedium),
              const SizedBox(height: 4),
              Text(
                'Manually add specific companies to scrape',
                style: theme.textTheme.bodySmall?.copyWith(
                  color: theme.colorScheme.onSurfaceVariant,
                ),
              ),
              const SizedBox(height: 8),
              Row(
                children: [
                  Expanded(
                    child: TextField(
                      controller: _companyController,
                      decoration: const InputDecoration(
                        hintText: 'Add a company...',
                        isDense: true,
                      ),
                      onSubmitted: (_) => _addCompany(),
                    ),
                  ),
                  const SizedBox(width: 8),
                  IconButton(
                    icon: const Icon(Icons.add_circle),
                    onPressed: _addCompany,
                  ),
                ],
              ),
              const SizedBox(height: 8),
              Wrap(
                spacing: 8,
                runSpacing: 4,
                children: _companies
                    .map((c) => Chip(
                          label: Text(c),
                          onDeleted: () => setState(() {
                            _companies.remove(c);
                            _selectedSuggestions.remove(c);
                          }),
                        ))
                    .toList(),
              ),
              if (_companies.isEmpty && _selectedSectors.isEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Text(
                    'Add companies or select sectors to scrape',
                    style: TextStyle(color: theme.colorScheme.error, fontSize: 12),
                  ),
                ),

              const SizedBox(height: 16),
              SwitchListTile(
                title: const Text('Set as default'),
                value: _isDefault,
                onChanged: (v) => setState(() => _isDefault = v),
              ),
              const SizedBox(height: 24),
              ElevatedButton(
                onPressed: _isSubmitting ? null : _submit,
                child: _isSubmitting
                    ? const SizedBox(
                        height: 20,
                        width: 20,
                        child: CircularProgressIndicator(strokeWidth: 2),
                      )
                    : const Text('Create Config'),
              ),
            ],
          ),
        ),
      ),
    );
  }
}
