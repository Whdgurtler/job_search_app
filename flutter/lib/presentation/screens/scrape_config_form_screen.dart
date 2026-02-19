import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/scrape_provider.dart';

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

  Future<void> _submit() async {
    if (!_formKey.currentState!.validate()) return;
    if (_companies.isEmpty) {
      ScaffoldMessenger.of(context).showSnackBar(
        const SnackBar(content: Text('Add at least one company')),
      );
      return;
    }

    setState(() => _isSubmitting = true);

    final success = await ref.read(scrapeConfigProvider.notifier).createConfig(
          name: _nameController.text.trim(),
          keywords: _keywordsController.text.trim(),
          companies: _companies,
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
              const SizedBox(height: 16),

              // Companies
              Text('Companies', style: Theme.of(context).textTheme.titleMedium),
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
                          onDeleted: () => setState(() => _companies.remove(c)),
                        ))
                    .toList(),
              ),
              if (_companies.isEmpty)
                Padding(
                  padding: const EdgeInsets.only(top: 4),
                  child: Text(
                    'Add at least one company to scrape',
                    style: TextStyle(color: Theme.of(context).colorScheme.error, fontSize: 12),
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
