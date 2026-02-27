import 'dart:convert';
import 'dart:io';

import 'package:dio/io.dart';

// ---------------------------------------------------------------------------
// In-memory cache for resolved IPs (cleared on app restart).
// ---------------------------------------------------------------------------
final Map<String, String> _dohCache = {};

/// Resolves [hostname] to an IPv4 address using Google's DNS-over-HTTPS API.
///
/// The lookup itself must not rely on the phone's default DNS (which is
/// blocked), so we bootstrap the HTTPS connection to `dns.google` by
/// connecting directly to its well-known IP `8.8.8.8`.
///
/// Falls back to normal OS DNS resolution if DoH fails (e.g. the device is
/// completely offline), ensuring the app degrades gracefully.
Future<String> resolveViaDoH(String hostname) async {
  if (_dohCache.containsKey(hostname)) {
    return _dohCache[hostname]!;
  }

  try {
    final ip = await _performDohLookup(hostname)
        .timeout(const Duration(seconds: 5));
    _dohCache[hostname] = ip;
    return ip;
  } catch (_) {
    // DoH itself failed or timed out — fall through to normal DNS below.
  }

  // Graceful fallback: let the OS resolve it the normal way.
  final addresses = await InternetAddress.lookup(hostname);
  final ip = addresses.first.address;
  _dohCache[hostname] = ip;
  return ip;
}

/// Performs the raw DNS-over-HTTPS lookup against Google's `dns.google`.
///
/// Separated from [resolveViaDoH] so that the caller can wrap this with a
/// `.timeout()` to cap how long the DoH lookup is allowed to take.
Future<String> _performDohLookup(String hostname) async {
  final client = HttpClient();

  // Override DNS for the DoH endpoint itself — connect to 8.8.8.8 directly
  // so that the ISP's broken resolver is never hit.
  client.connectionFactory = (Uri uri, String? proxyHost, int? proxyPort) {
    final targetHost = uri.host == 'dns.google' ? '8.8.8.8' : uri.host;
    return Socket.startConnect(targetHost, uri.port);
  };

  final uri = Uri.https(
    'dns.google',
    '/resolve',
    {'name': hostname, 'type': 'A'},
  );

  try {
    final request = await client.getUrl(uri);
    request.headers.set('Accept', 'application/dns-json');
    final response = await request.close();

    if (response.statusCode == 200) {
      final body = await response.transform(utf8.decoder).join();
      final json = jsonDecode(body) as Map<String, dynamic>;
      final answers = json['Answer'] as List<dynamic>?;
      if (answers != null && answers.isNotEmpty) {
        final aRecord = answers.firstWhere(
          (a) => (a as Map<String, dynamic>)['type'] == 1,
          orElse: () => answers.first,
        ) as Map<String, dynamic>;
        return aRecord['data'] as String;
      }
    }
    throw Exception('No A record found for $hostname');
  } finally {
    client.close();
  }
}

/// Builds a [IOHttpClientAdapter] that intercepts outgoing connections to
/// [targetHost] and routes them to the IP returned by [resolveViaDoH].
///
/// Because we operate at the raw TCP layer (`Socket.startConnect`),
/// the `HttpClient` handles the TLS upgrade itself and automatically
/// uses the original URI host as the SNI server name — so Railway's
/// HTTPS certificate validates correctly even though we connected by IP.
IOHttpClientAdapter buildDohAdapter(String targetHost) {
  return IOHttpClientAdapter(
    createHttpClient: () {
      final client = HttpClient();
      client.idleTimeout = const Duration(seconds: 3);

      client.connectionFactory =
          (Uri uri, String? proxyHost, int? proxyPort) async {
        if (uri.host == targetHost) {
          // Resolve the IP via DoH, bypassing the ISP's broken DNS.
          final ip = await resolveViaDoH(targetHost);
          return Socket.startConnect(ip, uri.port);
        }

        // For any other host (e.g. image CDNs), use normal resolution.
        return Socket.startConnect(uri.host, uri.port);
      };

      return client;
    },
  );
}
