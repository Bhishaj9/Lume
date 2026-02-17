# Riverpod Link Resolver Provider

This Riverpod provider connects your Flutter app to the FastAPI backend at `http://localhost:8000/resolve/{query}`.

## Files Created

```
lib/
├── data/models/
│   └── lume_link_model.dart           # LumeLink model with parsing
├── presentation/providers/
│   ├── link_resolver_provider.dart    # Main FutureProvider
│   └── providers.dart                 # Export file
└── main.dart                          # Updated with ProviderScope
```

## Usage Example

```dart
import 'package:flutter/material.dart';
import 'package:flutter_riverpod/flutter_riverpod.dart';
import 'presentation/providers/link_resolver_provider.dart';

class MovieDetailScreen extends ConsumerWidget {
  final String movieTitle;

  const MovieDetailScreen({super.key, required this.movieTitle});

  @override
  Widget build(BuildContext context, WidgetRef ref) {
    // Watch the provider with the movie title
    final linkAsync = ref.watch(linkResolverProvider(movieTitle));

    return Scaffold(
      appBar: AppBar(title: Text(movieTitle)),
      body: linkAsync.when(
        data: (link) => Column(
          children: [
            Text(link.title),
            Text('Size: ${link.formattedSize}'),
            Text('Seeds: ${link.seeds}'),
            Text('Health: ${link.healthLabel}'),
            ElevatedButton(
              onPressed: () {
                // Open the URL
                // launchUrl(Uri.parse(link.url));
              },
              child: const Text('Open Link'),
            ),
          ],
        ),
        loading: () => const Center(
          child: CircularProgressIndicator(),
        ),
        error: (error, stack) {
          final exception = error as LinkResolverException;
          return Center(
            child: Column(
              mainAxisAlignment: MainAxisAlignment.center,
              children: [
                Icon(
                  exception.code == 'BACKEND_OFFLINE'
                      ? Icons.cloud_off
                      : Icons.error_outline,
                  size: 64,
                  color: Colors.grey,
                ),
                const SizedBox(height: 16),
                Text(
                  exception.message,
                  textAlign: TextAlign.center,
                  style: const TextStyle(color: Colors.grey),
                ),
                const SizedBox(height: 16),
                ElevatedButton(
                  onPressed: () {
                    // Refresh the provider
                    ref.invalidate(linkResolverProvider(movieTitle));
                  },
                  child: const Text('Retry'),
                ),
              ],
            ),
          );
        },
      ),
    );
  }
}
```

## Provider Details

### `linkResolverProvider`

**Type:** `FutureProvider.family<LumeLinkModel, String>`

**Parameters:**
- `movieTitle` (String): The movie title to search for

**Returns:** `LumeLinkModel`
- `title`: Movie title
- `url`: Direct URL
- `size`: Size in bytes (nullable)
- `seeds`: Health indicator

**Error Handling:**

The provider throws `LinkResolverException` with these codes:
- `BACKEND_OFFLINE`: FastAPI server is not running
- `NOT_FOUND`: No results found for the query
- `NETWORK_ERROR`: General network issues
- `UNKNOWN_ERROR`: Unexpected errors

### `dioProvider`

**Type:** `Provider<Dio>`

Configured to connect to `http://localhost:8000` with:
- 5-second connection timeout
- 10-second receive timeout
- JSON content-type headers

**Note for Android Emulator:**
Use `10.0.2.2:8000` instead of `localhost:8000`:

```dart
final dioProvider = Provider<Dio>((ref) {
  return Dio(
    BaseOptions(
      baseUrl: 'http://10.0.2.2:8000', // Android emulator
      // ...
    ),
  );
});
```

## LumeLinkModel Extension Methods

```dart
final link = LumeLinkModel(...);

// Formatted size: "8.5 GB"
print(link.formattedSize);

// Health status
print(link.health); // LinkHealth.excellent/good/fair/poor
print(link.healthLabel); // "Excellent"
```

## Running the App

1. **Start the FastAPI backend:**
```bash
cd lume_backend
python main.py
```

2. **Install Flutter dependencies:**
```bash
flutter pub get
```

3. **Run the Flutter app:**
```bash
flutter run
```

## Testing

Test the provider with different queries:

```dart
// Works - returns top result
ref.watch(linkResolverProvider('Inception'));

// Returns all mock results
ref.watch(linkResolverProvider('all'));

// Triggers 404 error
ref.watch(linkResolverProvider('empty'));
```

## Architecture

```
UI (ConsumerWidget)
    ↓
linkResolverProvider (Riverpod)
    ↓
dioProvider (Dio HTTP client)
    ↓
FastAPI Backend (localhost:8000)
    ↓
Returns LumeLinkModel
```

This architecture provides:
- **Automatic caching**: Riverpod caches results
- **Error handling**: Custom exceptions with error codes
- **Testability**: Easy to mock providers
- **Type safety**: Pydantic-style validation
