import 'package:dio/dio.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';

import '../../core/exceptions/backend_exceptions.dart';
import '../../core/network/api_config.dart';
import '../../core/network/doh_client.dart';
import '../../data/models/lume_link_model.dart';

/// Whether the app is running against the real production backend.
///
/// In development / emulator builds [apiBaseUrl] still points to 10.0.2.2
/// so DoH is unnecessary (and would fail to connect to a loopback address).
bool get _isProduction => apiBaseUrl.contains('railway.app');

/// Extracts the hostname from [apiBaseUrl], e.g.
///   "https://lume-production-967e.up.railway.app" → "lume-production-967e.up.railway.app"
String get _productionHost => Uri.parse(apiBaseUrl).host;

/// Dio client provider.
///
/// In production builds a custom [IOHttpClientAdapter] is attached that
/// resolves the Railway backend via DNS-over-HTTPS, bypassing ISP-level
/// DNS blocks present on some Indian carriers.
final dioProvider = FutureProvider<Dio>((ref) async {
  final dio = Dio(
    BaseOptions(
      baseUrl: apiBaseUrl,
      connectTimeout: const Duration(seconds: 30),
      receiveTimeout: const Duration(seconds: 30),
    ),
  );

  if (_isProduction) {
    // Warm up the DoH cache eagerly so the first real API call is instant.
    await resolveViaDoH(_productionHost).catchError((_) => '');
    dio.httpClientAdapter = buildDohAdapter(_productionHost);
  }

  return dio;
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

  // dioProvider is now a FutureProvider — await it.
  final dio = await ref.watch(dioProvider.future);

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
