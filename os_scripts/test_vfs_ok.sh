#!/bin/bash
# Повторная проверка трёх вариантов VFS успешными командами.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== minimal ==="
python3 -m src.emulator \
    --vfs "$ROOT/vfs/minimal" \
    --log "$ROOT/logs/ok_minimal.xml" \
    --script "$ROOT/scripts/startup_minimal.txt"

echo "=== several ==="
python3 -m src.emulator \
    --vfs "$ROOT/vfs/several" \
    --log "$ROOT/logs/ok_several.xml" \
    --script "$ROOT/scripts/startup_ok.txt"

echo "=== deep ==="
python3 -m src.emulator \
    --vfs "$ROOT/vfs/deep" \
    --log "$ROOT/logs/ok_deep.xml" \
    --script "$ROOT/scripts/startup_deep_ok.txt"
