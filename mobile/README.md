# ARQYV Mobile

This directory contains the scaffold for future mobile clients of ARQYV.

## Architecture Decision

The mobile clients communicate with an **ARQYV local API server** (FastAPI, runs alongside the desktop app)
exposing REST + WebSocket endpoints for:

- Search queries
- File browsing
- Thumbnail streaming
- Playback control (remote)

## Options

### Flutter (Recommended)
- Single codebase → iOS + Android + Web
- High-performance Dart rendering
- Rich widget ecosystem matching the Qt desktop look

```
flutter/
├── lib/
│   ├── main.dart
│   ├── screens/
│   │   ├── home_screen.dart
│   │   ├── search_screen.dart
│   │   └── player_screen.dart
│   ├── widgets/
│   ├── models/
│   └── services/
│       ├── api_service.dart
│       └── search_service.dart
└── pubspec.yaml
```

### React Native (Alternative)
- JS/TS ecosystem, familiar if you use React on web
- Expo for rapid prototyping

```
react_native/
├── src/
│   ├── screens/
│   ├── components/
│   ├── hooks/
│   └── api/
├── App.tsx
└── package.json
```

## Getting Started (Flutter)

```bash
cd mobile/flutter
flutter pub get
flutter run
```

The app expects the desktop ARQYV to expose:
- `http://localhost:8765/api/v1` – REST API
- `ws://localhost:8765/ws` – WebSocket updates
