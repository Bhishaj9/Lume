import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/exceptions/backend_exceptions.dart';
import '../../core/network/api_config.dart';
import '../../data/models/lume_link_model.dart';

final dioProvider = Provider<Dio>((ref) {
  return Dio(
    BaseOptions(
      baseUrl: apiBaseUrl,
      connectTimeout: const Duration(seconds: 5),
      receiveTimeout: const Duration(seconds: 15),
    ),
  );
});

class LinkResolverCache extends StateNotifier<Map<String, LumeLinkModel>> {
  LinkResolverCache() : super(const {});

  LumeLinkModel? get(String query) => state[query];

  void put(String query, LumeLinkModel link) {
    state = {...state, query: link};
  }

  void clear() => state = const {};
}

final linkResolverCacheProvider =
    StateNotifierProvider<LinkResolverCache, Map<String, LumeLinkModel>>(
  (ref) => LinkResolverCache(),
);

final linkResolverProvider = FutureProvider.autoDispose
    .family<LumeLinkModel, String>((ref, query) async {
  final cache = ref.read(linkResolverCacheProvider.notifier);
  final cached = cache.get(query);
  if (cached != null) return cached;

  final dio = ref.watch(dioProvider);

  try {
    final response = await dio.get<Map<String, dynamic>>('/resolve/$query');
    final data = response.data ?? <String, dynamic>{};
    final link = LumeLinkModel.fromJson(data);

    if (!link.isHealthy) {
      throw const NoHealthyMagnetException(
        'No healthy magnet link is currently available.',
      );
    }

    cache.put(query, link);
    return link;
  } on DioException catch (error) {
    final statusCode = error.response?.statusCode;
    if (statusCode != null) {
      throw BackendHttpException(
        statusCode: statusCode,
        message: 'Backend request failed with status $statusCode',
      );
    }
    rethrow;
  }
});
