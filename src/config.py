"""Разбор параметров командной строки эмулятора."""

import argparse
from argparse import Namespace

UNSET = "(не задан)"


def parse_args(argv: list[str] | None = None) -> Namespace:
    """Читает путь к VFS, лог-файлу и стартовому скрипту."""
    parser = argparse.ArgumentParser(
        description="Эмулятор командной оболочки ОС",
    )
    parser.add_argument(
        "--vfs",
        dest="vfs_path",
        default=None,
        help="Путь к физическому расположению VFS",
    )
    parser.add_argument(
        "--log",
        dest="log_path",
        default=None,
        help="Путь к XML-файлу журнала команд",
    )
    parser.add_argument(
        "--script",
        dest="script_path",
        default=None,
        help="Путь к стартовому скрипту эмулятора",
    )
    return parser.parse_args(argv)


def format_param(value: str | None) -> str:
    """Возвращает значение параметра или пометку, что он не задан."""
    if value is None:
        return UNSET
    return value


def print_config(args: Namespace) -> None:
    """Печатает отладочный вывод всех параметров запуска."""
    print("Параметры запуска:")
    print(f"  Путь к VFS: {format_param(args.vfs_path)}")
    print(f"  Путь к лог-файлу: {format_param(args.log_path)}")
    print(f"  Путь к стартовому скрипту: {format_param(args.script_path)}")
