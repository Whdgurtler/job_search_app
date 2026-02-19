import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'package:go_router/go_router.dart';
import '../providers/auth_provider.dart';
import '../providers/user_provider.dart';

class ProfileScreen extends ConsumerWidget {
  const ProfileScreen({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final authState = ref.watch(authProvider);
    final profileState = ref.watch(userProfileProvider);

    return Scaffold(
      appBar: AppBar(
        title: const Text('Profile'),
        leading: IconButton(
          icon: const Icon(Icons.arrow_back),
          onPressed: () => context.go('/jobs'),
        ),
        actions: [
          IconButton(
            icon: const Icon(Icons.logout),
            onPressed: () async {
              await ref.read(authProvider.notifier).signOut();
            },
          ),
        ],
      ),
      body: profileState.isLoading
          ? const Center(child: CircularProgressIndicator())
          : SingleChildScrollView(
              padding: const EdgeInsets.all(16),
              child: Column(
                crossAxisAlignment: CrossAxisAlignment.center,
                children: [
                  CircleAvatar(
                    radius: 50,
                    backgroundColor: Theme.of(context).colorScheme.primary,
                    child: Text(
                      (authState.user?.displayName?.substring(0, 1) ??
                              authState.user?.email?.substring(0, 1) ??
                              'U')
                          .toUpperCase(),
                      style: const TextStyle(fontSize: 36, color: Colors.white),
                    ),
                  ),
                  const SizedBox(height: 16),
                  Text(
                    authState.user?.displayName ?? 'User',
                    style: Theme.of(context).textTheme.headlineSmall,
                  ),
                  const SizedBox(height: 4),
                  Text(
                    authState.user?.email ?? '',
                    style: Theme.of(context).textTheme.bodyMedium,
                  ),
                  const SizedBox(height: 32),
                  Card(
                    child: Column(
                      children: [
                        ListTile(
                          leading: const Icon(Icons.email),
                          title: const Text('Email'),
                          subtitle: Text(authState.user?.email ?? ''),
                        ),
                        const Divider(),
                        ListTile(
                          leading: const Icon(Icons.person),
                          title: const Text('Display Name'),
                          subtitle:
                              Text(authState.user?.displayName ?? 'Not set'),
                          trailing: const Icon(Icons.edit),
                          onTap: () => _showEditDisplayNameDialog(context, ref),
                        ),
                        const Divider(),
                        ListTile(
                          leading: const Icon(Icons.phone),
                          title: const Text('Phone Number'),
                          subtitle:
                              Text(authState.user?.phoneNumber ?? 'Not set'),
                          trailing: const Icon(Icons.edit),
                          onTap: () => _showEditPhoneDialog(context, ref),
                        ),
                      ],
                    ),
                  ),
                  const SizedBox(height: 16),
                  Card(
                    child: Column(
                      children: [
                        ListTile(
                          leading: const Icon(Icons.description),
                          title: const Text('Resume'),
                          subtitle: Text(
                            profileState.user?.resumeUrl != null
                                ? 'Uploaded'
                                : 'No resume uploaded',
                          ),
                          trailing: IconButton(
                            icon: const Icon(Icons.upload_file),
                            onPressed: () => context.go('/resume-upload'),
                          ),
                        ),
                      ],
                    ),
                  ),
                  if (profileState.error != null) ...[
                    const SizedBox(height: 16),
                    Text(
                      profileState.error!,
                      style: TextStyle(
                        color: Theme.of(context).colorScheme.error,
                      ),
                    ),
                  ],
                ],
              ),
            ),
    );
  }

  void _showEditDisplayNameDialog(BuildContext context, WidgetRef ref) {
    final controller = TextEditingController(
      text: ref.read(authProvider).user?.displayName,
    );

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Edit Display Name'),
        content: TextField(
          controller: controller,
          decoration: const InputDecoration(
            labelText: 'Display Name',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              ref.read(userProfileProvider.notifier).updateProfile(
                    displayName: controller.text,
                  );
              Navigator.pop(context);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }

  void _showEditPhoneDialog(BuildContext context, WidgetRef ref) {
    final controller = TextEditingController(
      text: ref.read(authProvider).user?.phoneNumber,
    );

    showDialog(
      context: context,
      builder: (context) => AlertDialog(
        title: const Text('Edit Phone Number'),
        content: TextField(
          controller: controller,
          keyboardType: TextInputType.phone,
          decoration: const InputDecoration(
            labelText: 'Phone Number',
          ),
        ),
        actions: [
          TextButton(
            onPressed: () => Navigator.pop(context),
            child: const Text('Cancel'),
          ),
          TextButton(
            onPressed: () {
              ref.read(userProfileProvider.notifier).updateProfile(
                    phoneNumber: controller.text,
                  );
              Navigator.pop(context);
            },
            child: const Text('Save'),
          ),
        ],
      ),
    );
  }
}
