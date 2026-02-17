import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/exceptions/backend_exceptions.dart';
import '../../core/network/connectivity_provider.dart';
import 'link_resolver_provider.dart';

final tmdbMovieProvider =
    FutureProvider.autoDispose.family<Map<String, dynamic>, String>(
  (ref, movieId) async {
    final isOnline = await ref.watch(internetStatusProvider.future);
    if (!isOnline) {
      throw const NoInternetException(
        'No internet connection. Check your connection and try again.',
      );
    }

    final dio = ref.watch(dioProvider);
    final response = await dio.get<Map<String, dynamic>>('/tmdb/$movieId');
    return response.data ?? <String, dynamic>{};
  },
);
