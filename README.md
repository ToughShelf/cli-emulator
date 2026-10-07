# Shell Emulator — эмулятор командной оболочки ОС

Учебный проект: эмулятор оболочки UNIX-подобной ОС (Вариант 29).
Этап 3 — виртуальная файловая система (VFS).

## Требования

- Python 3.10 или выше
- Запуск из корня проекта

## Быстрый старт

```bash
chmod +x run.sh
./run.sh
```

Параметры командной строки:

```bash
python3 -m src.emulator \
    --vfs vfs/deep \
    --log logs/session.xml \
    --script scripts/startup_all.txt
```

| Параметр   | Назначение                          |
|------------|-------------------------------------|
| `--vfs`    | Путь к физическому расположению VFS |
| `--log`    | Путь к XML-файлу журнала команд     |
| `--script` | Путь к стартовому скрипту           |

При запуске печатаются все заданные параметры. Имя VFS в приглашении
берётся из последнего компонента пути `--vfs` либо равно `vfs`.

## Структура проекта

```
PythonProject1/
├── src/
│   ├── __init__.py
│   ├── config.py
│   ├── emulator.py
│   ├── logger.py
│   ├── main.py
│   └── vfs.py
├── scripts/
│   ├── startup_empty.txt
│   ├── startup_minimal.txt
│   ├── startup_ok.txt
│   ├── startup_deep_ok.txt
│   ├── startup_errors.txt
│   └── startup_all.txt
├── os_scripts/
│   ├── test_defaults.sh
│   ├── test_params.sh
│   ├── test_errors.sh
│   ├── test_vfs_variants.sh
│   ├── test_vfs_ok.sh
│   └── test_vfs_errors.sh
├── vfs/
│   ├── minimal/
│   ├── several/
│   └── deep/
├── tests/
│   └── __init__.py
├── README.md
├── .gitignore
└── run.sh
```

## VFS

Источник VFS — директория на диске. При старте дерево каталогов и
содержимое файлов копируются в память; исходная директория не
изменяется. Все операции `ls` и `cd` работают только с копией в памяти.

Варианты для проверки:

| Каталог        | Описание                                      |
|----------------|-----------------------------------------------|
| `vfs/minimal`  | Минимальный набор файлов                      |
| `vfs/several`  | Несколько файлов и подкаталог                 |
| `vfs/deep`     | Не менее трёх уровней (`home/user/docs/...`)  |

## Команды

| Команда | Описание | Пример |
|---------|----------|--------|
| `ls [opts] [path...]` | Список файлов/каталогов VFS | `ls -la /home` |
| `cd [path]` | Смена текущего каталога VFS | `cd /home/user` |
| `exit` | Выход из эмулятора | `exit` |

Ключи `ls`: `-l` (подробный вывод), `-a` (скрытые записи).

## Стартовый скрипт

Файл выполняется до интерактивного режима. Комментарии — как в Python
(`#`). На экран выводятся приглашение с командой и ответ эмулятора.

Полный сценарий этапов 1–3: `scripts/startup_all.txt`.

## Журнал XML

Каждое событие вызова команды содержит дату и время, имя пользователя,
имя команды и аргументы.

## Проверка

```bash
chmod +x os_scripts/*.sh
./os_scripts/test_defaults.sh
./os_scripts/test_params.sh
./os_scripts/test_errors.sh
./os_scripts/test_vfs_variants.sh
./os_scripts/test_vfs_ok.sh
./os_scripts/test_vfs_errors.sh
```

## Этапы

### Этап 1 — REPL

- CLI, приглашение с именем VFS, парсер, `ls`/`cd`/`exit`

### Этап 2 — конфигурация

- Параметры `--vfs`, `--log`, `--script`
- Отладочный вывод параметров
- XML-лог вызовов команд
- Стартовый скрипт с комментариями

### Этап 3 — VFS (текущий)

- Загрузка VFS из директории в память
- Рабочие `ls` и `cd` по дереву VFS
- Тестовые варианты: minimal, several, deep
