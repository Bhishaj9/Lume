#!/usr/bin/env bash
# ============================================================
# Lume — Production APK Build Script
# ============================================================
#
# Usage:
#     chmod +x build_production.sh
#     ./build_production.sh
# ============================================================

API_URL="https://lume-production-967e.up.railway.app"

echo "Building Lume APK for production..."
echo "API_URL = $API_URL"
echo ""

flutter build apk --release --dart-define=API_URL="$API_URL"

echo ""
echo "✅ Done! APK is at build/app/outputs/flutter-apk/app-release.apk"
