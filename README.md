# Lume

[![Project Status](https://img.shields.io/badge/Project%20Status-MVP%20Completed-success)](https://github.com/Bhishaj9/Lume)
[![Flutter Version](https://img.shields.io/badge/Flutter-3.x-blue?logo=flutter)](https://flutter.dev)
[![License](https://img.shields.io/badge/License-MIT-yellow.svg)](LICENSE)

A Minimalist, Material 3 Streaming Engine built with Flutter and FastAPI.

<p align="center">
  <img src="assets/images/splash_logo.png" alt="Lume Logo" width="200"/>
</p>

## 📸 Screenshots

<p align="center">
  <em>Coming Soon - App screenshots will be added here</em>
</p>

<!--
| Home Screen | Movie Details | Player | Search |
|------------|---------------|---------|---------|
| ![Home](screenshots/home.png) | ![Details](screenshots/details.png) | ![Player](screenshots/player.png) | ![Search](screenshots/search.png) |
-->

## ✨ Features

**Sprint 1: True Black Foundation**  
OLED-optimized True Black (#000000) backgrounds, Material 3 theming with Google Fonts Inter.

**Sprint 2: Monet Dynamic Theme**  
Palette extraction from movie posters with automatic accent color shifting, Material 3 ColorScheme generation.

**Sprint 3: P2P Streaming Engine**  
P2P streaming with flutter_go_stream_engine, magnet link resolution via FastAPI backend.

**Sprint 4: Continue Watching**  
Isar database for local watch history, progress tracking with 30-second auto-save intervals.

**Sprint 5: TV Show Support**  
Season/episode selection with SxxExx format, dual-prefetching metadata and links at 80% playback.

**Sprint 6: Smart Cache Management**  
Auto-cleanup with 48-hour aging, 5GB threshold management, protection for active "Continue Watching" sessions.

## 🛠️ Tech Stack

### Frontend
- **Flutter 3.x** - Cross-platform UI framework
- **Material 3 Monet** - Dynamic theming with palette extraction
- **Riverpod** - State management and dependency injection
- **Isar** - High-performance local database
- **P2P Streaming** - Peer-to-peer content delivery
- **CachedNetworkImage** - Efficient image caching

### Backend
- **FastAPI** - Modern, fast Python web framework
- **PirateBayAPI** - P2P search integration
- **TMDB API** - Movie and TV metadata
- **Python 3.8+** - Async backend services

### Streaming
- **flutter_go_stream_engine** - Native P2P streaming
- **video_player** - ExoPlayer integration with gestures
- **Screen Brightness & Volume Control** - Immersive playback controls

## 🔐 Security

**API Key Management**

All sensitive API keys and tokens are managed via environment variables using `.env` files. **Never commit your `.env` file to version control.**

```bash
# .env file (ignored by git)
TMDB_API_KEY=your_api_key_here
TMDB_READ_ACCESS_TOKEN=your_token_here
```

The repository includes:
- `.env.example` - Template showing required variables
- `.gitignore` - Prevents accidental commits of `.env` files
- Runtime validation - App throws clear errors if keys are missing

## 🚀 Setup

### Prerequisites
- Flutter 3.x SDK
- Python 3.8+
- TMDB API Key ([Get one here](https://www.themoviedb.org/settings/api))

### Backend

```bash
cd lume_backend
python -m venv venv
source venv/bin/activate  # Windows: venv\Scripts\activate
pip install -r requirements.txt

# Create environment file
cp .env.example .env
# Edit .env and add your TMDB_API_KEY

python main.py
```

The API runs on `http://localhost:8000`

### Frontend

```bash
# Install dependencies
flutter pub get

# Generate Isar models
flutter pub run build_runner build

# Run the app
flutter run
```

## 📁 Project Structure

```
lume/
├── lib/                          # Flutter application
│   ├── core/                     # Theme, network, utilities
│   ├── data/                     # Models and repositories
│   ├── domain/                   # Business logic
│   └── presentation/             # UI screens and widgets
├── lume_backend/                 # FastAPI backend
│   ├── providers/                # Data providers
│   ├── routers/                  # API endpoints
│   └── models/                   # Pydantic schemas
├── assets/                       # Images and fonts
└── .env.example                  # Environment template
```

## 🎯 Roadmap

- [x] True Black OLED theme
- [x] Material 3 Monet dynamic colors
- [x] P2P streaming
- [x] Continue watching with Isar
- [x] TV Show season/episode support
- [x] Smart cache management
- [ ] User authentication
- [ ] Cloud sync
- [ ] Casting support

---

Built with ❤️ for the streaming experience.
