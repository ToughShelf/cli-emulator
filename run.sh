#!/bin/bash

if ! command -v python3 >/dev/null 2>&1; then
    echo "Ошибка: Python 3 не установлен"
    exit 1
fi

python3 -m src.emulator "$@"
