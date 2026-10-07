#!/bin/bash
# Проверка VFS: минимальный, несколько файлов, три уровня.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== VFS minimal ==="
python3 -m src.emulator \
    --vfs "$ROOT/vfs/minimal" \
    --log "$ROOT/logs/vfs_minimal.xml" \
    --script "$ROOT/scripts/startup_minimal.txt"

echo "=== VFS several ==="
python3 -m src.emulator \
    --vfs "$ROOT/vfs/several" \
    --log "$ROOT/logs/vfs_several.xml" \
    --script "$ROOT/scripts/startup_ok.txt"

echo "=== VFS deep ==="
python3 -m src.emulator \
    --vfs "$ROOT/vfs/deep" \
    --log "$ROOT/logs/vfs_deep.xml" \
    --script "$ROOT/scripts/startup_all.txt"
