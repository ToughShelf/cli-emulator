#!/bin/bash
# Проверка стартового скрипта с ошибками и полным набором флагов.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Скрипт с ошибками ==="
python3 -m src.emulator \
    --vfs "$ROOT/vfs/minimal" \
    --log "$ROOT/logs/errors.xml" \
    --script "$ROOT/scripts/startup_errors.txt"

echo "=== Повтор со всеми параметрами ==="
python3 -m src.emulator \
    --vfs "$ROOT/vfs/deep" \
    --log "$ROOT/logs/errors_full.xml" \
    --script "$ROOT/scripts/startup_errors.txt"
