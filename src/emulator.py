"""Эмулятор командной оболочки ОС. Этап 2: конфигурация."""

import shlex
from pathlib import Path

from src.config import parse_args, print_config
from src.logger import XmlCommandLogger

DEFAULT_VFS_NAME = "vfs"
COMMENT_PREFIX = "#"


class ShellEmulator:
    """Интерактивный прототип оболочки с командами-заглушками."""

    def __init__(
        self,
        vfs_path: str | None,
        log_path: str | None,
        script_path: str | None,
    ) -> None:
        """Сохраняет параметры запуска и регистрирует команды."""
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.vfs_name = self._vfs_name(vfs_path)
        self.logger = XmlCommandLogger(log_path)
        self.running = True
        self.commands = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "exit": self.cmd_exit,
        }

    def _vfs_name(self, vfs_path: str | None) -> str:
        """Берёт имя VFS из пути или значение по умолчанию."""
        if vfs_path is None:
            return DEFAULT_VFS_NAME
        name = Path(vfs_path).name
        if name:
            return name
        return DEFAULT_VFS_NAME

    def cmd_ls(self, args: list[str]) -> None:
        """Заглушка ls: печатает имя команды и аргументы."""
        print(f"[ls] аргументы: {args}")

    def cmd_cd(self, args: list[str]) -> None:
        """Заглушка cd: печатает имя команды и аргументы."""
        print(f"[cd] аргументы: {args}")

    def cmd_exit(self, args: list[str]) -> None:
        """Завершает работу эмулятора."""
        print("Завершение работы эмулятора...")
        self.running = False

    def parse_input(self, line: str) -> tuple[str | None, list[str]]:
        """Разделяет ввод на команду и аргументы по пробелам."""
        try:
            tokens = shlex.split(line)
        except ValueError as error:
            message = f"ошибка разбора команды: {error}"
            raise ValueError(message) from error
        if not tokens:
            return None, []
        command, *args = tokens
        return command, args

    def _parse_line(self, line: str) -> tuple[str, list[str]] | None:
        """Возвращает команду или печатает ошибку разбора."""
        try:
            command, args = self.parse_input(line)
        except ValueError as error:
            print(f"Ошибка: {error}")
            self.logger.log("parse_error", [str(error)])
            return None
        if command is None:
            return None
        return command, args

    def execute(self, line: str) -> None:
        """Разбирает строку, логирует вызов и выполняет команду."""
        line = line.strip()
        if not line:
            return
        parsed = self._parse_line(line)
        if parsed is None:
            return
        command, args = parsed
        self.logger.log(command, args)
        handler = self.commands.get(command)
        if handler is None:
            print(f"{command}: команда не найдена")
            return
        handler(args)

    def run_startup_script(self, script_path: str) -> None:
        """Выполняет стартовый скрипт, показывая ввод и вывод."""
        try:
            with open(script_path, encoding="utf-8") as file:
                lines = file.readlines()
        except OSError as error:
            print(f"Ошибка: не удалось прочитать скрипт: {error}")
            return
        for raw_line in lines:
            if not self.running:
                break
            if self._is_ignored_line(raw_line):
                continue
            command_line = raw_line.rstrip("\n")
            print(f"{self.vfs_name}$ {command_line}")
            self.execute(command_line)

    def _is_ignored_line(self, line: str) -> bool:
        """Пропускает пустые строки и комментарии языка Python."""
        stripped = line.strip()
        if not stripped:
            return True
        return stripped.startswith(COMMENT_PREFIX)

    def run(self) -> None:
        """Запускает цикл чтения команд из стандартного ввода."""
        while self.running:
            try:
                line = input(f"{self.vfs_name}$ ")
            except EOFError:
                print()
                break
            except KeyboardInterrupt:
                print()
                continue
            self.execute(line)
            if not self.running:
                break

    def start(self) -> None:
        """Сначала выполняет стартовый скрипт, затем REPL."""
        if self.script_path is not None:
            self.run_startup_script(self.script_path)
        if self.running:
            self.run()


def main() -> None:
    """Точка входа: печатает параметры и запускает эмулятор."""
    args = parse_args()
    print_config(args)
    emulator = ShellEmulator(
        vfs_path=args.vfs_path,
        log_path=args.log_path,
        script_path=args.script_path,
    )
    emulator.start()


if __name__ == "__main__":
    main()
