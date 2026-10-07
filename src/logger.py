"""XML-журнал вызовов команд эмулятора."""

from datetime import datetime
from getpass import getuser
from pathlib import Path
from xml.etree import ElementTree as et

LOG_ROOT_TAG = "log"
EVENT_TAG = "event"
UNKNOWN_USER = "unknown"


def current_user() -> str:
    """Возвращает имя пользователя операционной системы."""
    try:
        return getuser()
    except OSError:
        return UNKNOWN_USER


class XmlCommandLogger:
    """Пишет события вызова команд в XML-файл."""

    def __init__(self, log_path: str | None) -> None:
        """Сохраняет путь к журналу. None отключает запись."""
        self.log_path = log_path

    def log(self, command: str, args: list[str]) -> None:
        """Добавляет в журнал событие вызова команды."""
        if self.log_path is None:
            return
        path = Path(self.log_path)
        path.parent.mkdir(parents=True, exist_ok=True)
        root = self._load_root(path)
        event = et.SubElement(root, EVENT_TAG)
        et.SubElement(event, "timestamp").text = (
            datetime.now().isoformat(timespec="seconds")
        )
        et.SubElement(event, "user").text = current_user()
        et.SubElement(event, "command").text = command
        et.SubElement(event, "args").text = " ".join(args)
        et.indent(root)
        tree = et.ElementTree(root)
        tree.write(path, encoding="utf-8", xml_declaration=True)

    def _load_root(self, path: Path) -> et.Element:
        """Читает корень журнала или создаёт пустой документ."""
        if not path.is_file():
            return et.Element(LOG_ROOT_TAG)
        try:
            root = et.parse(path).getroot()
        except et.ParseError:
            return et.Element(LOG_ROOT_TAG)
        if root.tag != LOG_ROOT_TAG:
            return et.Element(LOG_ROOT_TAG)
        return root
