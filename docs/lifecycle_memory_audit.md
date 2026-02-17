# Lifecycle & Memory Audit (Flutter Video Player)

Date: 2026-02-17

## Requested Scope
- `lib/presentation/pages/video_player_page.dart`
- Related Riverpod providers (especially `linkResolverProvider`)

## Repository Reality Check
This repository snapshot does **not** include a Flutter `lib/` source tree, including the target `video_player_page.dart` and provider implementation files. As a result, the checks below cannot be confirmed against concrete Dart code in this checkout.

---

## Task 1: Resource Disposal Audit
**Goal:** Verify `VideoPlayerController`, `ChewieController`, and `StreamSubscription` (torrent status) are always cancelled in `dispose()`.

### Status
⚠️ **Blocked in this snapshot** — target file is missing.

### What must be true in code
- `@override void dispose()` exists in `VideoPlayerPage` state class.
- `_torrentStatusSubscription?.cancel()` (or equivalent) is called.
- `_chewieController?.dispose()` is called.
- `_videoPlayerController?.dispose()` is called.
- Disposal happens before `super.dispose()`.
- Any listeners added to controllers are removed/cancelled.

---

## Task 2: 3-Second Ghost HUD Timer Safety
**Goal:** Ensure timer is cancelled when page is popped to avoid `setState` on unmounted widget.

### Status
⚠️ **Blocked in this snapshot** — timer implementation is not present.

### What must be true in code
- Store timer in a field (e.g., `_ghostHudTimer`).
- Cancel timer in `dispose()` via `_ghostHudTimer?.cancel()`.
- Before scheduling a new timer, cancel previous timer to avoid overlap.
- Timer callback guards state updates with `if (!mounted) return;` before `setState`.

---

## Task 3: Riverpod Lifecycle (`linkResolverProvider`)
**Goal:** Verify `linkResolverProvider` uses `.autoDispose`.

### Status
⚠️ **Blocked in this snapshot** — provider implementation file is missing.

### Risk if not `autoDispose`
If `linkResolverProvider` is a plain `FutureProvider.family` without `autoDispose`, provider state can persist beyond screen lifetime and retain resolved links/magnet metadata in memory after the user exits player UI. This can:
- Increase memory retention across navigation sessions.
- Keep sensitive/temporary link values in process memory longer than intended.
- Cause stale link reuse in subsequent sessions unless explicitly invalidated.

### Recommended shape
Use `FutureProvider.autoDispose.family<...>` (or equivalent generated Riverpod annotation with auto-disposal), and only add cache retention windows intentionally via `ref.keepAlive()` when justified.

---

## Task 4: Auto-Play Next Transition Leak Check
**Goal:** Ensure previous controllers are fully disposed before initializing new playback instance.

### Status
⚠️ **Blocked in this snapshot** — transition logic is not present.

### What must be true in code
In the auto-play-next flow:
1. Pause/stop old playback.
2. Cancel old torrent status subscription(s).
3. Dispose old `ChewieController`.
4. Dispose old `VideoPlayerController`.
5. Null out stale refs.
6. Initialize new controllers.
7. Rebind listeners/subscriptions for new media only.

A helper like `_disposeCurrentPlayback()` called before `_initializePlayback(nextItem)` is the safest pattern.

---

## Commands Used For This Audit
- `rg --files | rg 'video_player_page\\.dart|video.*player.*page\\.dart'`
- `rg -n "linkResolverProvider|VideoPlayerController|ChewieController|Ghost HUD|autoDispose|Auto-Play Next|torrent status|StreamSubscription|video_player" -S`

## Evidence in Existing Docs
- Existing pre-deployment audit already records missing Flutter `lib/` source and inability to verify `linkResolverProvider` implementation in this snapshot.
