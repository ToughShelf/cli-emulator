#!/bin/bash
# Ошибки команд на минимальном, среднем и глубоком VFS.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== errors / minimal ==="
python3 -m src.emulator \
    --vfs "$ROOT/vfs/minimal" \
    --log "$ROOT/logs/err_minimal.xml" \
    --script "$ROOT/scripts/startup_errors.txt"

echo "=== errors / several ==="
python3 -m src.emulator \
    --vfs "$ROOT/vfs/several" \
    --log "$ROOT/logs/err_several.xml" \
    --script "$ROOT/scripts/startup_errors.txt"

echo "=== errors / deep ==="
python3 -m src.emulator \
    --vfs "$ROOT/vfs/deep" \
    --log "$ROOT/logs/err_deep.xml" \
    --script "$ROOT/scripts/startup_errors.txt"
