# Production Environment Audit (Lume)

Date: 2026-02-17

## Task 1: Dynamic Base URL (`lib/core/network/`)

### Findings
- The current repository snapshot does **not** include the Flutter `lib/` directory, so `lib/core/network/` could not be directly inspected.
- A hardcoded emulator URL (`http://10.0.2.2:8000`) exists in implementation guidance docs, which indicates production risk if copied as-is into app code.

### Recommendation
Use compile-time environment values and a small environment config class so Dev/Prod switching does not require source edits.

```dart
// lib/core/network/app_env.dart
class AppEnv {
  static const String env = String.fromEnvironment('APP_ENV', defaultValue: 'dev');
  static const String apiBaseUrl = String.fromEnvironment(
    'API_BASE_URL',
    defaultValue: 'http://10.0.2.2:8000',
  );

  static bool get isProd => env == 'prod';
}
```

Then consume in your HTTP client/provider:

```dart
final dio = Dio(BaseOptions(baseUrl: AppEnv.apiBaseUrl));
```

Run targets:

```bash
# Dev
flutter run --dart-define=APP_ENV=dev --dart-define=API_BASE_URL=http://10.0.2.2:8000

# Prod
flutter build apk --release --dart-define=APP_ENV=prod --dart-define=API_BASE_URL=https://api.yourdomain.com
```

If runtime mutability is required (without rebuild), use a config asset (`assets/config/prod.json`, `assets/config/dev.json`) selected by `APP_ENV`.

## Task 2: Worker Scaling (`lume_backend/main.py`)

### Findings
- `main.py` uses `uvicorn.run(..., reload=True)` inside `__main__`, which is appropriate for development only.
- Production should use CLI startup with worker processes.

### Recommended production command

```bash
uvicorn lume_backend.main:app --host 0.0.0.0 --port 8000 --workers 4 --log-level info
```

Notes:
- Keep `--reload` disabled in production.
- Tune worker count by CPU and traffic profile (start around `2 x CPU cores` or benchmark-driven values).

## Task 3: `.env.example` parity check

### Findings
- Backend code currently does not read required environment variables.
- Existing `.env.example` referenced TMDB keys that are not consumed by current backend code, creating setup drift.

### Action taken
- Updated `.env.example` to reflect current reality:
  - No required backend environment keys today.
  - Added optional deployment placeholders for production host/port/worker settings.

Result: New server setup is now plug-and-play for the current codebase and less misleading.
