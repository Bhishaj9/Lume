# Asset & Binary Optimization Audit (APK size + log hardening)

Date: 2026-02-17

## Scope Reviewed
- `pubspec.yaml`
- `android/app/src/main/AndroidManifest.xml`
- repository root image assets (`splash_logo.png`, `icon_foreground.png`)
- Dart/Android source tree presence for release-log stripping controls

## Task 1 — Proguard & Obfuscation (Release)

The repository snapshot does not currently include `android/app/build.gradle`, so the exact block below should be added to that file's `buildTypes { release { ... } }` section.

```gradle
android {
  ...
  buildTypes {
    release {
      // Keep your existing signingConfig if already configured
      signingConfig signingConfigs.release

      // Enable shrinking/obfuscation for smaller + harder-to-reverse APKs
      minifyEnabled true
      shrinkResources true

      // Use default optimized rules + app-specific keep rules
      proguardFiles getDefaultProguardFile('proguard-android-optimize.txt'), 'proguard-rules.pro'
    }
  }
}
```

Recommended Flutter release build command (for additional Dart obfuscation):

```bash
flutter build apk --release --obfuscate --split-debug-info=build/symbols
```

Notes:
- `minifyEnabled true` + `shrinkResources true` reduces Java/Kotlin bytecode and strips unused resources.
- `--obfuscate --split-debug-info` obfuscates Dart symbols while preserving crash-symbol mapping externally.

## Task 2 — Font & Image Stripping

### Findings
1. `pubspec.yaml` declares broad asset directories (`assets/images/`, `assets/fonts/`), but those folders are not present in this snapshot; this should be corrected to prevent asset packaging drift and confusion.
2. Two image files larger than 1MB exist and are strong APK-size risk factors:
   - `splash_logo.png` ≈ 4.3MB
   - `icon_foreground.png` ≈ 4.7MB
3. No active custom font family is registered under `flutter.fonts` (currently commented out), so no bundled TTFs are being intentionally packaged from this config snapshot.

### Optimizations to keep install size under ~50MB
- Move images into `assets/images/` and only include files that are actually used.
- Re-export `splash_logo.png` to target max edge around 1024px (or less for splash), then compress (pngquant/tinyPNG/Squoosh).
- Re-export `icon_foreground.png` to Android adaptive icon recommended size and strip metadata.
- If image quality allows, convert large static artwork from PNG to WebP (`cwebp -q 80`).
- Prefer explicit asset entries over directory globs once asset list stabilizes, e.g.:
  ```yaml
  flutter:
    assets:
      - assets/images/splash_logo.webp
      - assets/images/icon_foreground.webp
  ```
- Keep icon/splash source files outside runtime asset bundle if only used by generators (`flutter_launcher_icons`, `flutter_native_splash`).

## Task 3 — Release-Mode Logging

The Flutter `lib/` tree is not present in this snapshot, so direct replacement of `print()` in Dart sources cannot be completed here. Use this release-safe logging policy in app code:

```dart
import 'package:flutter/foundation.dart';

void appLog(String message) {
  if (kDebugMode) {
    debugPrint(message);
  }
}
```

And enforce in CI/local checks:

```bash
rg -n "\bprint\(" lib test
```

Android-side hardening recommendation:
- Keep `android:debuggable` unset/false for release.
- Avoid logging secrets from platform channels.

Observed in this repo snapshot:
- No Dart files were present to scan.
- One backend dev `print()` exists in `lume_backend/providers/mock_provider.py` and should not be promoted to production logging paths.

## Commands Used
- `rg --files`
- `sed -n '1,260p' pubspec.yaml`
- `find . -type f -size +1M | sort`
- `du -h splash_logo.png icon_foreground.png`
- `rg -n "\bprint\(|debugPrint\(|developer\.log\(|\blog\(" --glob '*.dart' --glob '*.kt' --glob '*.java' --glob '*.py'`
