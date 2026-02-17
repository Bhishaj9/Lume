# Dynamic Color (Monet) Engine for Lume

A comprehensive Material 3 Monet implementation that extracts colors from movie posters and applies them throughout the UI.

## Architecture Overview

```
Movie Poster
    ↓
DynamicThemeProvider (palette_generator)
    ↓
ColorScheme.fromSeed(seedColor: extracted)
    ↓
MaterialApp Theme
    ↓
All UI Components
```

## Key Features

### 1. Palette Extraction (Task 1)

**File:** `lib/core/theme/dynamic_theme_provider.dart`

The `DynamicThemeProvider` uses `PaletteGenerator` to extract the dominant/vibrant color from movie posters:

```dart
final palette = await PaletteGenerator.fromImageProvider(
  NetworkImage(posterUrl),
  size: const Size(200, 300),
  maximumColorCount: 20,
);

Color extractedColor = palette.vibrantColor?.color ??
    palette.dominantColor?.color ??
    fallbackColor;
```

**Priority:**
1. Vibrant color (most saturated)
2. Dominant color (most common)
3. Netflix red (fallback)

### 2. Theme Integration (Task 2)

**File:** `lib/main.dart`

The `MaterialApp` is now a `ConsumerWidget` that watches the dynamic theme:

```dart
class LumeApp extends ConsumerWidget {
  @override
  Widget build(BuildContext context, WidgetRef ref) {
    final themeState = ref.watch(dynamicThemeProvider);
    
    return MaterialApp(
      theme: ThemeData(colorScheme: themeState.colorScheme),
      darkTheme: ThemeData(colorScheme: themeState.colorScheme),
    );
  }
}
```

This ensures the entire app responds to theme changes.

### 3. Seamless Transitions (Task 3)

**File:** `lib/presentation/pages/movie_details_page.dart`

When a movie is opened:

```dart
@override
void initState() {
  super.initState();
  // Extract theme from poster
  _extractTheme();
}

@override
void dispose() {
  // Reset to default when leaving
  ref.read(dynamicThemeProvider.notifier).resetToDefault();
  super.dispose();
}
```

**Play FAB** uses the dynamic accent color:
```dart
final accentColor = ref.watch(accentColorProvider);

AnimatedContainer(
  duration: const Duration(milliseconds: 300),
  decoration: BoxDecoration(
    color: accentColor,
    boxShadow: [
      BoxShadow(
        color: accentColor.withOpacity(0.4),
      ),
    ],
  ),
)
```

### 4. True Black OLED Override (Task 4)

Even with dynamic colors, the background remains True Black:

```dart
ColorScheme.fromSeed(
  seedColor: extractedColor,
  brightness: Brightness.dark,
  // Force True Black
  surface: const Color(0xFF000000),
  background: const Color(0xFF000000),
  onSurface: Colors.white,
  onBackground: Colors.white,
)
```

## Color Enhancement

Colors are automatically enhanced for OLED displays:

```dart
Color _enhanceColorForOLED(Color color) {
  final hsl = HSLColor.fromColor(color);
  
  // Minimum 60% saturation for vibrancy
  final saturation = hsl.saturation < 0.6 ? 0.6 : hsl.saturation;
  
  // Constrain lightness between 30-70%
  final lightness = hsl.lightness < 0.3 ? 0.3 : 
      (hsl.lightness > 0.7 ? 0.7 : hsl.lightness);
  
  return hsl
    .withSaturation(saturation)
    .withLightness(lightness)
    .toColor();
}
```

## Usage

### In Any Widget

```dart
// Get current accent color
final accentColor = ref.watch(accentColorProvider);

// Or get full color scheme
final colorScheme = ref.watch(dynamicThemeProvider).colorScheme;

// Use in widgets
Container(
  color: accentColor,
  child: Text('Hello', style: TextStyle(color: colorScheme.onPrimary)),
)
```

### Programmatically Extract Theme

```dart
// Extract from any image
await ref.read(dynamicThemeProvider.notifier)
    .extractThemeFromImage(imageUrl);

// Reset to default
ref.read(dynamicThemeProvider.notifier).resetToDefault();
```

## Color Palette Reference

When you open a movie, the following colors are generated:

| Color | Source | Usage |
|-------|--------|-------|
| Primary | Extracted from poster | Play button, progress bars |
| Primary Container | 20% lighter | Elevated buttons |
| Secondary | Complementary | Secondary actions |
| Tertiary | Analogous | Highlights |
| Surface | True Black (#000000) | Backgrounds |
| On Surface | White | Text on black |

## Animation

The Play FAB smoothly transitions between colors:

```dart
AnimatedContainer(
  duration: const Duration(milliseconds: 300),
  color: accentColor,
)
```

## Dependencies

```yaml
dependencies:
  palette_generator: ^0.3.3+3
  flutter_riverpod: ^2.4.9
```

## Performance

- Palette extraction happens once when movie details page opens
- 200x300px image used for faster processing
- Maximum 20 colors analyzed
- Theme updates trigger minimal rebuilds via Riverpod

## Example Flow

```
1. User taps "Inception" movie card
2. MovieDetailsPage opens
3. initState() calls _extractTheme()
4. PaletteGenerator analyzes poster (200ms)
5. DynamicThemeNotifier updates state
6. MaterialApp rebuilds with new ColorScheme
7. Play button smoothly animates to poster's blue color
8. User leaves page → theme resets to Netflix red
```

## Notes

- **True Black is enforced** - surface/background always #000000
- **Colors are enhanced** - minimum 60% saturation for OLED vibrancy
- **Fallback included** - Netflix red if extraction fails
- **Auto-cleanup** - theme resets when leaving movie page
- **Smooth transitions** - 300ms animation for color changes
