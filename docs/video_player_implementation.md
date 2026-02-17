# Video Player Implementation

A custom video player with Media3/ExoPlayer-style gestures and minimalist Material 3 HUD.

## Features

### 1. Video Player Controller (Task 1)
- Uses `video_player` package for video playback
- Auto-plays in landscape mode (fullscreen)
- Supports network streaming URLs from torrent

### 2. Gesture Overlays (Task 2)

#### Vertical Drag - Left Side (0-50% of screen)
- **Action**: Adjust screen brightness
- **Package**: `screen_brightness`
- **Visual**: Shows brightness icon with vertical progress bar

#### Vertical Drag - Right Side (50-100% of screen)
- **Action**: Adjust system volume
- **Package**: `volume_controller`
- **Visual**: Shows volume icon with vertical progress bar

#### Horizontal Double Tap
- **Left 1/3**: Seek backward 10 seconds
- **Right 1/3**: Seek forward 10 seconds
- **Visual**: Shows circular seek indicators with icons

### 3. Minimalist HUD (Task 3)

#### Controls
- **Close Button**: Small 'X' icon in top-left corner
- **Title**: Movie title displayed at top-center
- **Seek Bar**: Material 3 thin slider at bottom
  - Muted accent color (60% opacity)
  - 3dp track height
  - Small 6dp thumb
- **Time**: Current time / Total duration below slider

#### Auto-Hide
- Controls automatically hide after 2 seconds of inactivity
- Tap anywhere to show controls again
- Timer resets on any interaction

## Usage

```dart
Navigator.push(
  context,
  MaterialPageRoute(
    builder: (context) => VideoPlayerPage(
      videoUrl: 'http://127.0.0.1:8080/video.mp4',
      title: 'Inception (2010)',
    ),
  ),
);
```

## Dependencies

Add to `pubspec.yaml`:

```yaml
dependencies:
  video_player: ^2.8.1
  screen_brightness: ^0.2.2+1
  volume_controller: ^2.0.7
```

## Implementation Details

### Screen Orientation
```dart
// Enters landscape on init
SystemChrome.setPreferredOrientations([
  DeviceOrientation.landscapeLeft,
  DeviceOrientation.landscapeRight,
]);

// Restores on dispose
SystemChrome.setPreferredOrientations([
  DeviceOrientation.portraitUp,
  DeviceOrientation.portraitDown,
]);
```

### Gesture Detection
```dart
GestureDetector(
  onVerticalDragUpdate: (details) {
    if (details.globalPosition.dx < screenWidth / 2) {
      // Left side - brightness
    } else {
      // Right side - volume
    }
  },
  onDoubleTap: () {
    // Seek logic
  },
)
```

### Material 3 Slider
```dart
SliderTheme(
  data: SliderTheme.of(context).copyWith(
    activeTrackColor: mutedAccent,      // 60% opacity
    inactiveTrackColor: Colors.white24,
    thumbColor: mutedAccent,
    trackHeight: 3,                      // Thin
    thumbShape: RoundSliderThumbShape(
      enabledThumbRadius: 6,             // Small
    ),
  ),
  child: Slider(...),
)
```

## Gestures Reference

| Gesture | Area | Action | Visual Feedback |
|---------|------|--------|----------------|
| Vertical Drag | Left 50% | Brightness | Icon + Vertical bar |
| Vertical Drag | Right 50% | Volume | Icon + Vertical bar |
| Double Tap | Left 1/3 | Seek -10s | Replay icon |
| Double Tap | Right 1/3 | Seek +10s | Forward icon |
| Single Tap | Center | Play/Pause | Pause/Play icon |
| Single Tap | Anywhere | Show/Hide HUD | Controls fade in/out |

## Customization

### Slider Color
Change the muted accent color:
```dart
final mutedAccent = theme.colorScheme.primary.withOpacity(0.6);
```

### Auto-Hide Duration
```dart
_hideTimer = Timer(const Duration(seconds: 2), () {
  // Hide controls
});
```

### Seek Duration
```dart
void _seekForward() {
  final newPosition = currentPosition + const Duration(seconds: 10);
  _controller.seekTo(newPosition);
}
```

## Notes

1. **Platform Support**: Android only (requires torrent streamer)
2. **Permissions**: Requires storage and network permissions
3. **Fullscreen**: Automatically enters immersive mode
4. **Clean Up**: Properly disposes controller and restores orientation
