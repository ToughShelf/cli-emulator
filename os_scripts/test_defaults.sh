#!/bin/bash
# Проверка запуска без параметров и со всеми параметрами.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Без параметров ==="
python3 -m src.emulator <<'EOF'
exit
EOF

echo "=== Все параметры ==="
python3 -m src.emulator \
    --vfs "$ROOT/vfs/minimal" \
    --log "$ROOT/logs/defaults.xml" \
    --script "$ROOT/scripts/startup_minimal.txt"
