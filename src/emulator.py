"""Эмулятор командной оболочки ОС. Этап 1: REPL-прототип."""

import sys
import shlex

DEFAULT_VFS_NAME = "vfs"
VFS_NAME_ARG_INDEX = 1


class ShellEmulator:
    """Интерактивный прототип оболочки с командами-заглушками."""

    def __init__(self, vfs_name: str) -> None:
        """Сохраняет имя VFS и регистрирует доступные команды."""
        self.vfs_name = vfs_name
        self.running = True
        self.commands = {
            "ls": self.cmd_ls,
            "cd": self.cmd_cd,
            "exit": self.cmd_exit,
        }

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

    def execute(self, line: str) -> None:
        """Разбирает строку и вызывает соответствующую команду."""
        line = line.strip()
        if not line:
            return

        try:
            command, args = self.parse_input(line)
        except ValueError as error:
            print(f"Ошибка: {error}")
            return

        if command is None:
            return

        handler = self.commands.get(command)
        if handler is None:
            print(f"{command}: команда не найдена")
            return

        handler(args)

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


def main() -> None:
    """Точка входа CLI: имя VFS берётся из аргумента или по умолчанию."""
    if len(sys.argv) > VFS_NAME_ARG_INDEX:
        vfs_name = sys.argv[VFS_NAME_ARG_INDEX]
    else:
        vfs_name = DEFAULT_VFS_NAME
    emulator = ShellEmulator(vfs_name)
    emulator.run()


if __name__ == "__main__":
    main()
