# Resource Efficiency Audit (Battery + OLED)

Date: 2026-02-17

## Requested Scope
- Home page repaint behavior (`RepaintBoundary` around frequently updating controls)
- Video player repaint behavior (`Seek Bar` / `Timer` updates)
- Android wake-lock lifecycle behavior (acquire only while actively playing)
- Poster image memory constraints (`CachedNetworkImage` with `memCacheHeight` / `memCacheWidth`)

## Repository Reality Check
This repository snapshot does **not** include the Flutter `lib/` source tree where `Home`, `VideoPlayerPage`, and `CachedNetworkImage` widgets would normally live. That prevents direct code verification for repaint boundaries and image cache dimension caps.

What is present:
- Android manifest permissions, including `WAKE_LOCK`.
- Architecture/docs that describe video player behavior, but not executable Dart source.

---

## Task 1: Repaint Boundaries (Home + VideoPlayer)
**Question:** Are we using `RepaintBoundary` so the full screen does not repaint when only seek bar/timer changes?

### Status
⚠️ **Blocked in this snapshot** — no `lib/` UI source files are available to inspect actual widget tree composition.

### Why this matters (battery + OLED)
Frequent updates (e.g., playback position every 250–1000ms) can trigger broad repaints if the seek bar and timer are not isolated. On OLED, this increases GPU compositing activity and power usage, especially with overlays and animations.

### Pass criteria to apply in code
- `VideoPlayerPage`: wrap seek bar/time cluster in `RepaintBoundary`.
- `Home`: wrap any rapidly changing strip/timer/progress widgets in `RepaintBoundary`.
- Ensure static regions (background/poster/title blocks) are not rebuilt on each playback tick.
- Prefer `ValueListenableBuilder`/`StreamBuilder` around only the small changing subtree.

---

## Task 2: CPU Wake-Locks (Android)
**Question:** Are we holding `WAKE_LOCK` only while video is actually playing, and releasing on pause/background?

### Status
⚠️ **Partially verifiable**
- ✅ Manifest declares `android.permission.WAKE_LOCK`.
- ⚠️ Runtime lifecycle handling is **not verifiable** without Flutter/native integration code (`lib/` and/or Android plugin wiring).

### Evidence in current checkout
- `WAKE_LOCK` permission is declared in `AndroidManifest.xml`.
- Foreground service for torrent streaming is declared, which can increase battery impact if not lifecycle-gated.

### Pass criteria to apply in code
- Acquire wake-lock **only** when playback state transitions to `playing`.
- Release wake-lock immediately when:
  - playback becomes `paused` or `stopped`,
  - app enters background/inactive (`AppLifecycleState.paused/inactive/detached`),
  - player screen is disposed.
- Avoid blanket wake-lock tied to service lifetime unless strictly required for active playback.
- Validate with logs around state transitions to ensure no leaked lock.

---

## Task 3: Image Caching (Poster Thumbnails)
**Question:** Are we capping `memCacheHeight` / `memCacheWidth` on `CachedNetworkImage` for small grid posters?

### Status
⚠️ **Blocked in this snapshot** — no Flutter UI image widget usage is present to inspect.

### Why this matters (RAM + battery)
Loading full-resolution artwork (e.g., 2160p/4K) for small cards wastes decode memory and CPU cycles, causing more GC pressure and higher energy use.

### Pass criteria to apply in code
- For grid/list poster thumbnails, set both:
  - `memCacheWidth` (roughly item width in physical pixels)
  - `memCacheHeight` (roughly item height in physical pixels)
- Optionally set `maxWidthDiskCache` / `maxHeightDiskCache` for disk efficiency.
- Keep full-res only for detail/hero screens where visibly needed.

---

## Direct Findings Summary
1. `WAKE_LOCK` permission exists in manifest, but lifecycle-safe usage cannot be confirmed from this snapshot.
2. Repaint boundary usage for Home/Video player cannot be confirmed (UI source missing).
3. `CachedNetworkImage` cache dimension caps cannot be confirmed (UI source missing).

## Commands Used
- `rg --files`
- `rg -n "RepaintBoundary|Seek Bar|SeekBar|Timer|WAKE_LOCK|wake|CachedNetworkImage|memCacheHeight|memCacheWidth|VideoPlayer|Home|video_player" -S .`
- `sed -n '1,220p' android/app/src/main/AndroidManifest.xml`
- `sed -n '1,260p' docs/video_player_implementation.md`

## Recommended Next Step
Once the Flutter `lib/` tree is available in this checkout, run the same audit against:
- `lib/presentation/pages/home_page.dart`
- `lib/presentation/pages/video_player_page.dart`
- poster/grid widgets using `CachedNetworkImage`
- playback lifecycle hooks that toggle wake-lock
