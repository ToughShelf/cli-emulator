#!/bin/bash
# Проверка дополнительных команд этапа 5.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== stage 5 extra commands ==="
python3 -m src.emulator \
    --vfs "$ROOT/vfs/deep" \
    --log "$ROOT/logs/extra.xml" \
    --script "$ROOT/scripts/startup_extra.txt"
