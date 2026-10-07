#!/bin/bash
# Проверка основных команд этапа 4 на глубоком VFS.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== stage 4 commands ==="
python3 -m src.emulator \
    --vfs "$ROOT/vfs/deep" \
    --log "$ROOT/logs/commands.xml" \
    --script "$ROOT/scripts/startup_commands.txt"
