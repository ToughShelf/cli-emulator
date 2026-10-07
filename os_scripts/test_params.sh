#!/bin/bash
# Поочерёдная проверка каждого параметра командной строки.

set -euo pipefail
ROOT="$(cd "$(dirname "$0")/.." && pwd)"
cd "$ROOT"

echo "=== Только --vfs ==="
python3 -m src.emulator --vfs "$ROOT/vfs/several" <<'EOF'
ls
exit
EOF

echo "=== Только --log ==="
python3 -m src.emulator --log "$ROOT/logs/only_log.xml" <<'EOF'
ls
exit
EOF

echo "=== Только --script ==="
python3 -m src.emulator --script "$ROOT/scripts/startup_empty.txt"

echo "=== Все параметры ==="
python3 -m src.emulator \
    --vfs "$ROOT/vfs/several" \
    --log "$ROOT/logs/params.xml" \
    --script "$ROOT/scripts/startup_ok.txt"
