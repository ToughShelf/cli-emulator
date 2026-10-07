"""Виртуальная файловая система, загружаемая в память."""

from pathlib import Path

LS_LONG = "l"
LS_ALL = "a"
KNOWN_LS_FLAGS = frozenset({LS_LONG, LS_ALL})
MAX_CD_ARGS = 1
ROOT_PATH = "/"
PARENT_DIR = ".."
CURRENT_DIR = "."
HIDDEN_PREFIX = "."
DIR_MARK = "<dir>"
FILE_MARK = "<file>"
DEFAULT_FILE_MODE = 0o644
DEFAULT_DIR_MODE = 0o755
MODE_BITS = 0o777
OCTAL_BASE = 8
MODE_WIDTH = 3
CP_ARG_COUNT = 2
CHMOD_MIN_ARGS = 2


class VfsError(Exception):
    """Ошибка операции с виртуальной файловой системой."""


class VfsNode:
    """Узел дерева VFS: каталог или файл в памяти."""

    def __init__(
        self,
        name: str,
        is_dir: bool,
        content: bytes | None = None,
        mode: int | None = None,
    ) -> None:
        """Создаёт узел без обращения к диску."""
        self.name = name
        self.is_dir = is_dir
        self.content = content if content is not None else b""
        if mode is None:
            mode = DEFAULT_DIR_MODE if is_dir else DEFAULT_FILE_MODE
        self.mode = mode
        self.children: dict[str, VfsNode] = {}

    def clone(self, name: str | None = None) -> "VfsNode":
        """Глубокая копия узла в памяти."""
        node = VfsNode(
            name=self.name if name is None else name,
            is_dir=self.is_dir,
            content=bytes(self.content),
            mode=self.mode,
        )
        for child_name, child in self.children.items():
            node.children[child_name] = child.clone()
        return node


def _read_file(path: Path) -> bytes:
    """Читает файл в память один раз при загрузке VFS."""
    try:
        return path.read_bytes()
    except OSError:
        return b""


def _node_from_entry(entry: Path) -> VfsNode:
    """Строит узел по записи исходной директории."""
    if entry.is_dir():
        return VfsNode(name=entry.name, is_dir=True)
    return VfsNode(
        name=entry.name,
        is_dir=False,
        content=_read_file(entry),
    )


def _fill_dir(node: VfsNode, disk_path: Path) -> None:
    """Копирует дерево каталога в память, не меняя исходник."""
    try:
        entries = list(disk_path.iterdir())
    except OSError as error:
        text = f"не удалось прочитать {disk_path}: {error}"
        raise VfsError(text) from error
    entries.sort(key=lambda item: item.name)
    for entry in entries:
        child = _node_from_entry(entry)
        node.children[child.name] = child
        if child.is_dir:
            _fill_dir(child, entry)


def parse_ls_args(
    args: list[str],
) -> tuple[bool, bool, list[str]]:
    """Разбирает ключи -l/-a и пути для команды ls."""
    long_mode = False
    all_mode = False
    paths: list[str] = []
    for item in args:
        if item.startswith("-") and len(item) > 1:
            long_mode, all_mode = _apply_ls_flags(
                item[1:],
                long_mode,
                all_mode,
            )
        else:
            paths.append(item)
    return long_mode, all_mode, paths


def _apply_ls_flags(
    flags: str,
    long_mode: bool,
    all_mode: bool,
) -> tuple[bool, bool]:
    """Применяет символы ключа ls или сообщает об ошибке."""
    for char in flags:
        if char not in KNOWN_LS_FLAGS:
            raise VfsError(f"неизвестный ключ -- {char}")
        if char == LS_LONG:
            long_mode = True
        if char == LS_ALL:
            all_mode = True
    return long_mode, all_mode


class VirtualFileSystem:
    """Дерево VFS и текущий каталог, только в памяти."""

    def __init__(self, root: VfsNode) -> None:
        """Сохраняет корень и ставит текущий каталог в /."""
        self.root = root
        self.parts: list[str] = []

    @classmethod
    def empty(cls) -> "VirtualFileSystem":
        """Создаёт пустой корневой каталог в памяти."""
        return cls(VfsNode(name=ROOT_PATH, is_dir=True))

    @classmethod
    def load(cls, vfs_path: str | None) -> "VirtualFileSystem":
        """Загружает директорию пользователя в память."""
        if vfs_path is None:
            return cls.empty()
        source = Path(vfs_path)
        if not source.exists():
            text = f"{vfs_path}: нет такого файла или каталога"
            raise VfsError(text)
        if not source.is_dir():
            raise VfsError(f"{vfs_path}: не каталог")
        root = VfsNode(name=ROOT_PATH, is_dir=True)
        _fill_dir(root, source)
        return cls(root)

    @property
    def cwd_path(self) -> str:
        """Возвращает абсолютный путь текущего каталога."""
        if not self.parts:
            return ROOT_PATH
        return ROOT_PATH + "/".join(self.parts)

    def change_dir(self, path: str) -> None:
        """Меняет текущий каталог внутри дерева в памяти."""
        node, parts = self._resolve(path)
        if not node.is_dir:
            raise VfsError(f"{path}: не каталог")
        self.parts = parts

    def get_node(self, path: str) -> VfsNode:
        """Возвращает узел по пути внутри дерева в памяти."""
        node, _parts = self._resolve(path)
        return node

    def read_text(self, path: str) -> str:
        """Читает текстовое содержимое файла из VFS в памяти."""
        node = self.get_node(path)
        if node.is_dir:
            raise VfsError(f"{path}: это каталог")
        try:
            return node.content.decode("utf-8")
        except UnicodeDecodeError as error:
            text = f"{path}: не удалось декодировать как UTF-8"
            raise VfsError(text) from error

    def format_listing(
        self,
        node: VfsNode,
        long_mode: bool,
        all_mode: bool,
    ) -> list[str]:
        """Формирует строки вывода ls для узла в памяти."""
        if not node.is_dir:
            return [self._format_named(node.name, node, long_mode)]
        names = self._dir_names(node, all_mode)
        lines = []
        for name in names:
            entry = self._dir_entry(node, name)
            lines.append(self._format_named(name, entry, long_mode))
        return lines

    def _dir_names(self, node: VfsNode, all_mode: bool) -> list[str]:
        """Возвращает имена записей каталога."""
        names = sorted(node.children)
        if not all_mode:
            names = [
                name
                for name in names
                if not name.startswith(HIDDEN_PREFIX)
            ]
        if all_mode:
            names = [CURRENT_DIR, PARENT_DIR, *names]
        return names

    def _dir_entry(self, node: VfsNode, name: str) -> VfsNode:
        """Возвращает узел записи, включая . и .."""
        if name == CURRENT_DIR:
            return node
        if name == PARENT_DIR:
            return node
        return node.children[name]

    def _format_named(
        self,
        name: str,
        node: VfsNode,
        long_mode: bool,
    ) -> str:
        """Собирает обычную или подробную строку ls."""
        if not long_mode:
            return name
        mark = DIR_MARK if node.is_dir else FILE_MARK
        mode = format(node.mode & MODE_BITS, f"0{MODE_WIDTH}o")
        size = len(node.content)
        return f"{mark}\t{mode}\t{size}\t{name}"

    def chmod(self, path: str, mode: int) -> None:
        """Меняет права доступа узла только в памяти."""
        node = self.get_node(path)
        node.mode = mode & MODE_BITS

    def copy(self, source: str, dest: str) -> None:
        """Копирует файл или каталог внутри VFS в памяти."""
        src_node = self.get_node(source)
        dest_parts = self._split_parts(dest)
        if not dest_parts:
            raise VfsError(f"{dest}: нельзя заменить корень")
        try:
            dest_node = self.get_node(dest)
        except VfsError:
            dest_node = None
        if dest_node is not None and dest_node.is_dir:
            self._put_child(
                dest_parts,
                src_node.name,
                src_node,
                overwrite=False,
            )
            return
        parent_parts = dest_parts[:-1]
        new_name = dest_parts[-1]
        self._put_child(
            parent_parts,
            new_name,
            src_node,
            overwrite=True,
        )

    def _put_child(
        self,
        parent_parts: list[str],
        name: str,
        src_node: VfsNode,
        overwrite: bool,
    ) -> None:
        """Кладёт копию узла в каталог-родитель в памяти."""
        parent = self._node_by_parts(parent_parts)
        if not parent.is_dir:
            raise VfsError("путь назначения не каталог")
        existing = parent.children.get(name)
        if existing is not None and not overwrite:
            raise VfsError(f"{name}: уже существует")
        if existing is not None and existing.is_dir:
            raise VfsError(f"{name}: это каталог")
        parent.children[name] = src_node.clone(name=name)

    def _node_by_parts(self, parts: list[str]) -> VfsNode:
        """Возвращает узел по уже нормализованным частям пути."""
        node = self.root
        built: list[str] = []
        for piece in parts:
            if not node.is_dir:
                raise VfsError("путь не является каталогом")
            child = node.children.get(piece)
            if child is None:
                path = ROOT_PATH + "/".join(built + [piece])
                text = f"{path}: нет такого файла или каталога"
                raise VfsError(text)
            node = child
            built.append(piece)
        return node

    def _resolve(self, path: str) -> tuple[VfsNode, list[str]]:
        """Разыменовывает абсолютный или относительный путь."""
        parts = self._split_parts(path)
        node = self.root
        for piece in parts:
            if not node.is_dir:
                raise VfsError(f"{path}: не каталог")
            child = node.children.get(piece)
            if child is None:
                text = f"{path}: нет такого файла или каталога"
                raise VfsError(text)
            node = child
        return node, parts

    def _split_parts(self, path: str) -> list[str]:
        """Строит нормализованный список компонентов пути."""
        if path.startswith(ROOT_PATH):
            parts: list[str] = []
        else:
            parts = list(self.parts)
        for piece in path.split("/"):
            parts = self._step_part(parts, piece)
        return parts

    def _step_part(self, parts: list[str], piece: str) -> list[str]:
        """Применяет один компонент пути к списку частей."""
        if piece in ("", CURRENT_DIR):
            return parts
        if piece == PARENT_DIR:
            if parts:
                return parts[:-1]
            return parts
        return [*parts, piece]
