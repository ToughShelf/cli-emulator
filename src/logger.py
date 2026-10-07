"""XML-журнал вызовов команд эмулятора."""

from datetime import datetime
from getpass import getuser
from pathlib import Path
from xml.etree import ElementTree as ET

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
        event = ET.SubElement(root, EVENT_TAG)
        ET.SubElement(event, "timestamp").text = (
            datetime.now().isoformat(timespec="seconds")
        )
        ET.SubElement(event, "user").text = current_user()
        ET.SubElement(event, "command").text = command
        ET.SubElement(event, "args").text = " ".join(args)
        ET.indent(root)
        tree = ET.ElementTree(root)
        tree.write(path, encoding="utf-8", xml_declaration=True)

    def _load_root(self, path: Path) -> ET.Element:
        """Читает корень журнала или создаёт пустой документ."""
        if not path.is_file():
            return ET.Element(LOG_ROOT_TAG)
        try:
            root = ET.parse(path).getroot()
        except ET.ParseError:
            return ET.Element(LOG_ROOT_TAG)
        if root.tag != LOG_ROOT_TAG:
            return ET.Element(LOG_ROOT_TAG)
        return root
