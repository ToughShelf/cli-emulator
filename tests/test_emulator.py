"""Юнит-тесты парсера и команд-заглушек эмулятора."""

import io
import unittest
from contextlib import redirect_stdout

from src.emulator import ShellEmulator


class TestParseInput(unittest.TestCase):
    """Проверяет разбор командной строки на команду и аргументы."""

    def setUp(self) -> None:
        """Создаёт эмулятор с именем VFS по умолчанию."""
        self.shell = ShellEmulator("vfs")

    def test_simple_command(self) -> None:
        """Команда без аргументов распознаётся корректно."""
        command, args = self.shell.parse_input("ls")
        self.assertEqual(command, "ls")
        self.assertEqual(args, [])

    def test_command_with_arguments(self) -> None:
        """Аргументы отделяются от имени команды по пробелам."""
        command, args = self.shell.parse_input("ls -l /home")
        self.assertEqual(command, "ls")
        self.assertEqual(args, ["-l", "/home"])

    def test_empty_input(self) -> None:
        """Пустая строка не даёт имени команды."""
        command, args = self.shell.parse_input("   ")
        self.assertIsNone(command)
        self.assertEqual(args, [])

    def test_quoted_arguments(self) -> None:
        """Аргумент в кавычках сохраняется как одно значение."""
        command, args = self.shell.parse_input('cd "my folder"')
        self.assertEqual(command, "cd")
        self.assertEqual(args, ["my folder"])

    def test_parse_error_unclosed_quote(self) -> None:
        """Незакрытая кавычка приводит к ошибке разбора."""
        with self.assertRaises(ValueError) as ctx:
            self.shell.parse_input('ls "unterminated')
        self.assertIn("ошибка разбора команды", str(ctx.exception))


class TestCommands(unittest.TestCase):
    """Проверяет заглушки команд и обработку неизвестного ввода."""

    def setUp(self) -> None:
        """Создаёт эмулятор с заданным именем VFS."""
        self.shell = ShellEmulator("myvfs")

    def test_all_commands_registered(self) -> None:
        """В таблице команд есть ls, cd и exit."""
        self.assertEqual(set(self.shell.commands), {"ls", "cd", "exit"})

    def test_ls_stub_output(self) -> None:
        """Заглушка ls печатает своё имя и аргументы."""
        buf = io.StringIO()
        expected = "[ls] аргументы: ['-la', '/tmp']\n"
        with redirect_stdout(buf):
            self.shell.cmd_ls(["-la", "/tmp"])
        self.assertEqual(buf.getvalue(), expected)

    def test_cd_stub_output(self) -> None:
        """Заглушка cd печатает своё имя и аргументы."""
        buf = io.StringIO()
        expected = "[cd] аргументы: ['/tmp']\n"
        with redirect_stdout(buf):
            self.shell.cmd_cd(["/tmp"])
        self.assertEqual(buf.getvalue(), expected)

    def test_exit_stops_emulator(self) -> None:
        """Команда exit останавливает цикл REPL."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.shell.cmd_exit([])
        self.assertFalse(self.shell.running)
        self.assertIn("Завершение работы эмулятора", buf.getvalue())

    def test_unknown_command(self) -> None:
        """Неизвестная команда сообщает об ошибке."""
        buf = io.StringIO()
        with redirect_stdout(buf):
            self.shell.execute("foobar")
        self.assertEqual(buf.getvalue(), "foobar: команда не найдена\n")

    def test_prompt_uses_vfs_name(self) -> None:
        """Имя VFS сохраняется для приглашения к вводу."""
        self.assertEqual(self.shell.vfs_name, "myvfs")


if __name__ == "__main__":
    unittest.main()
