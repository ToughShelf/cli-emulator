"""Эмулятор командной оболочки ОС. Этап 5: доп. команды."""

import shlex
from pathlib import Path

from src.config import parse_args, print_config
from src.logger import XmlCommandLogger
from src.vfs import (
    CHMOD_MIN_ARGS,
    CP_ARG_COUNT,
    MAX_CD_ARGS,
    MODE_BITS,
    OCTAL_BASE,
    ROOT_PATH,
    VfsError,
    VirtualFileSystem,
    parse_ls_args,
)

DEFAULT_VFS_NAME = "vfs"
COMMENT_PREFIX = "#"
EMPTY_ARG_COUNT = 0

HELP_TEXT = {
    "ls": "список файлов и каталогов VFS (-l, -a)",
    "cd": "смена текущего каталога VFS",
    "echo": "печать аргументов",
    "cat": "вывод содержимого файлов",
    "rev": "строки файлов в обратном порядке",
    "chmod": "смена прав доступа в памяти VFS",
    "cp": "копирование файла или каталога в памяти",
    "help": "список команд и кратких описаний",
    "exit": "выход из эмулятора",
}


class ShellEmulator:
    """Эмулятор оболочки с командами UNIX-подобного CLI."""

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
        self.vfs = self._create_vfs(vfs_path)
        self.running = True
        self.commands = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "echo": self.cmd_echo,
            "cat": self.cmd_cat,
            "rev": self.cmd_rev,
            "chmod": self.cmd_chmod,
            "cp": self.cmd_cp,
            "help": self.cmd_help,
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

    def _create_vfs(self, vfs_path: str | None) -> VirtualFileSystem:
        """Загружает VFS в память или создаёт пустое дерево."""
        try:
            return VirtualFileSystem.load(vfs_path)
        except VfsError as error:
            print(f"VFS: {error}")
            return VirtualFileSystem.empty()

    def prompt(self) -> str:
        """Собирает приглашение с именем VFS и текущим путём."""
        return f"{self.vfs_name}:{self.vfs.cwd_path}$ "

    def cmd_ls(self, args: list[str]) -> None:
        """Печатает содержимое каталога или файл из VFS."""
        try:
            long_mode, all_mode, paths = parse_ls_args(args)
        except VfsError as error:
            print(f"ls: {error}")
            return
        if not paths:
            paths = [self.vfs.cwd_path]
        show_header = len(paths) > 1
        for path in paths:
            self._ls_one(path, long_mode, all_mode, show_header)

    def _ls_one(
        self,
        path: str,
        long_mode: bool,
        all_mode: bool,
        show_header: bool,
    ) -> None:
        """Печатает результат ls для одного пути."""
        try:
            node = self.vfs.get_node(path)
            lines = self.vfs.format_listing(
                node,
                long_mode,
                all_mode,
            )
        except VfsError as error:
            print(f"ls: {error}")
            return
        if show_header:
            print(f"{path}:")
        for line in lines:
            print(line)

    def cmd_cd(self, args: list[str]) -> None:
        """Меняет текущий каталог внутри VFS в памяти."""
        if len(args) > MAX_CD_ARGS:
            print("cd: слишком много аргументов")
            return
        target = args[0] if args else ROOT_PATH
        try:
            self.vfs.change_dir(target)
        except VfsError as error:
            print(f"cd: {error}")

    def cmd_echo(self, args: list[str]) -> None:
        """Печатает аргументы, разделённые пробелами."""
        print(" ".join(args))

    def cmd_cat(self, args: list[str]) -> None:
        """Печатает содержимое файлов из VFS."""
        if len(args) == EMPTY_ARG_COUNT:
            print("cat: не указан файл")
            return
        for path in args:
            self._print_file(path, reverse=False)

    def cmd_rev(self, args: list[str]) -> None:
        """Печатает строки файлов в обратном порядке символов."""
        if len(args) == EMPTY_ARG_COUNT:
            print("rev: не указан файл")
            return
        for path in args:
            self._print_file(path, reverse=True)

    def _print_file(self, path: str, reverse: bool) -> None:
        """Читает файл VFS и печатает его текст или ошибки."""
        try:
            text = self.vfs.read_text(path)
        except VfsError as error:
            name = "rev" if reverse else "cat"
            print(f"{name}: {error}")
            return
        for line in text.splitlines():
            print(line[::-1] if reverse else line)

    def cmd_chmod(self, args: list[str]) -> None:
        """Меняет права доступа узлов VFS только в памяти."""
        if len(args) < CHMOD_MIN_ARGS:
            print("chmod: нужны режим и путь")
            return
        try:
            mode = self._parse_mode(args[0])
        except VfsError as error:
            print(f"chmod: {error}")
            return
        for path in args[1:]:
            try:
                self.vfs.chmod(path, mode)
            except VfsError as error:
                print(f"chmod: {error}")

    def _parse_mode(self, text: str) -> int:
        """Разбирает восьмеричный режим доступа."""
        try:
            mode = int(text, OCTAL_BASE)
        except ValueError as error:
            message = f"неверный режим доступа: {text}"
            raise VfsError(message) from error
        return mode & MODE_BITS

    def cmd_cp(self, args: list[str]) -> None:
        """Копирует файл или каталог внутри VFS в памяти."""
        if len(args) != CP_ARG_COUNT:
            print("cp: нужны источник и назначение")
            return
        source, dest = args
        try:
            self.vfs.copy(source, dest)
        except VfsError as error:
            print(f"cp: {error}")

    def cmd_help(self, args: list[str]) -> None:
        """Печатает список команд и краткие описания."""
        if args:
            print("help: аргументы не используются")
        for name in sorted(HELP_TEXT):
            print(f"{name} — {HELP_TEXT[name]}")

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
            print(f"{self.prompt()}{command_line}")
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
                line = input(self.prompt())
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
