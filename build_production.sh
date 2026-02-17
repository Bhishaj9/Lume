#!/usr/bin/env bash
# ============================================================
# Lume — Production APK Build Script
# ============================================================
#
# ⚠️  IMPORTANT: Replace the placeholder URL below with your
#     actual Railway deployment URL before running this script.
#
#     Example: https://lume-production.up.railway.app
#
# Usage:
#     chmod +x build_production.sh
#     ./build_production.sh
# ============================================================

API_URL="https://your-railway-url.up.railway.app"

echo "Building Lume APK for production..."
echo "API_URL = $API_URL"
echo ""

flutter build apk --release --dart-define=API_URL="$API_URL"

echo ""
echo "✅ Done! APK is at build/app/outputs/flutter-apk/app-release.apk"
