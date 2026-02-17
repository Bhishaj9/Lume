import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import 'core/exceptions/backend_exceptions.dart';
import 'core/network/connectivity_provider.dart';
import 'presentation/pages/video_player_page.dart';
import 'presentation/providers/tmdb_provider.dart';
import 'presentation/widgets/no_internet_banner.dart';
import 'presentation/widgets/service_unavailable_screen.dart';

void main() {
  ErrorWidget.builder = (FlutterErrorDetails details) {
    final exception = details.exception;
    if (exception is BackendHttpException && exception.isServiceUnavailable) {
      return const MaterialApp(home: ServiceUnavailableScreen());
    }

    return MaterialApp(
      home: Scaffold(
        body: Center(child: Text('Unexpected UI error: $exception')),
      ),
    );
  };

  runApp(const ProviderScope(child: LumeApp()));
}

class LumeApp extends ConsumerWidget {
  const LumeApp({super.key});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    ref.listen<AsyncValue<bool>>(internetStatusProvider, (prev, next) {
      final justWentOffline = prev?.value == true && next.value == false;
      if (justWentOffline) {
        ScaffoldMessenger.of(context).showSnackBar(
          const SnackBar(content: Text('You are offline.')),
        );
      }
    });

    final internetState = ref.watch(internetStatusProvider);

    return MaterialApp(
      home: Scaffold(
        body: SafeArea(
          child: Column(
            children: [
              if (internetState.value == false) const NoInternetBanner(),
              Expanded(
                child: Center(
                  child: FilledButton(
                    onPressed: () {
                      Navigator.of(context).push(
                        MaterialPageRoute(
                          builder: (_) => const VideoPlayerPage(query: 'Inception'),
                        ),
                      );
                    },
                    child: const Text('Open Player'),
                  ),
                ),
              ),
              Consumer(
                builder: (context, ref, _) {
                  final tmdbState = ref.watch(tmdbMovieProvider('550'));
                  return tmdbState.when(
                    data: (_) => const SizedBox.shrink(),
                    loading: () => const Padding(
                      padding: EdgeInsets.all(12),
                      child: Text('Loading TMDB metadata...'),
                    ),
                    error: (error, stackTrace) => Padding(
                      padding: const EdgeInsets.all(12),
                      child: Text(
                        error is NoInternetException
                            ? error.message
                            : 'TMDB fetch failed: $error',
                      ),
                    ),
                  );
                },
              ),
            ],
          ),
        ),
      ),
    );
  }
}
