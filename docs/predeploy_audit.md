# Pre-Deployment Audit (Lume)

Date: 2026-02-17

## Scope Reviewed
- `lume_backend/main.py`
- `lume_backend/routers/media.py`
- `lume_backend/providers/base.py`
- `lume_backend/providers/mock_provider.py`
- `pirate_provider.py`
- `android/app/src/main/AndroidManifest.xml`
- `pubspec.yaml`
- `README.md`
- `docs/video_player_implementation.md`
- `docs/riverpod_provider_usage.md`
- `docs/lifecycle_memory_audit.md`

## Critical Bugs
1. CORS is overly permissive and misconfigured for credentials (`allow_origins=["*"]` with `allow_credentials=True`), which is unsafe and can violate browser CORS rules.
2. `pirate_provider.py` runs blocking provider calls (`PirateBayAPI.Search`, `PirateBayAPI.Download`) inside an `async` method without offloading, risking event-loop stalls under load.
3. `pirate_provider.py` appears structurally inconsistent with backend provider contracts (`.base_provider` import path and return shape differ from `BaseProvider` expected by API router).
4. `search_media` does not map `ProviderConnectionError` to 503 like `resolve_media`; connection faults can degrade to generic 500.
5. TV query formatter (`_format_tv_query`) has no guardrails for invalid season/episode values (e.g., 0 or negative), producing malformed queries.

## Performance Optimization
1. Replace blocking torrent provider calls with async/non-blocking wrappers (executor threads or async client).
2. Introduce provider instance reuse and pooling strategy (today each request builds a new provider via dependency function).
3. Add explicit HTTP timeout/retry/circuit-breaker strategy in production provider implementation.
4. Validate `limit` in `/resolve/search/{query}` with bounds to avoid expensive over-fetching.
5. For Flutter, verify actual `linkResolverProvider` uses `autoDispose` and configured cache windows (docs claim caching, but implementation file is not present in repo snapshot).

## Refactoring Advice
1. Consolidate duplicated exception-to-HTTP mapping logic across router endpoints.
2. Move query formatting and validation into a dedicated utility/service used by both router and providers.
3. Align repository structure so production torrent provider is under `lume_backend/providers/` and implements the same interface as mock provider.
4. Add explicit API-layer input validation for season/episode relationships (e.g., require both for episode-specific searches).
5. Convert implementation claims in docs/README (80% prefetch, smart cache aging) into checked code references or tests to avoid documentation drift.

## Known Gaps in This Repository Snapshot
- No Flutter `lib/` source was available to directly inspect:
  - `VideoPlayerPage` lifecycle disposal
  - `linkResolverProvider` implementation and cache tuning
  - 80% playback prefetch synchronization logic
  - Smart cache 48-hour aging implementation

These items should be re-audited once corresponding Dart code is added or shared.
