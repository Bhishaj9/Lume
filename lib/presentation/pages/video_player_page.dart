import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/exceptions/backend_exceptions.dart';
import '../providers/link_resolver_provider.dart';
import '../widgets/service_unavailable_screen.dart';

class VideoPlayerPage extends ConsumerWidget {
  const VideoPlayerPage({super.key, required this.query});

  final String query;

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final linkAsync = ref.watch(linkResolverProvider(query));

    return Scaffold(
      appBar: AppBar(title: Text(query)),
      body: linkAsync.when(
        loading: () => const Center(child: CircularProgressIndicator()),
        data: (link) => Center(
          child: Text('Ready to play: ${link.title}'),
        ),
        error: (error, stackTrace) {
          if (error is BackendHttpException && error.isServiceUnavailable) {
            return ServiceUnavailableScreen(
              onRetry: () => ref.invalidate(linkResolverProvider(query)),
            );
          }

          if (error is NoHealthyMagnetException) {
            return Center(
              child: Padding(
                padding: const EdgeInsets.all(24),
                child: Column(
                  mainAxisSize: MainAxisSize.min,
                  children: [
                    Text(error.message, textAlign: TextAlign.center),
                    const SizedBox(height: 16),
                    FilledButton(
                      onPressed: () {
                        ref.read(linkResolverCacheProvider.notifier).clear();
                        ref.invalidate(linkResolverProvider(query));
                      },
                      child: const Text('Try Again'),
                    ),
                  ],
                ),
              ),
            );
          }

          return Center(
            child: Text('Something went wrong: $error'),
          );
        },
      ),
    );
  }
}
