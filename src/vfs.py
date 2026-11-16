import os
from dataclasses import dataclass, field


@dataclass
class VFSNode:
    """In-memory node representing a file or directory in the VFS."""

    name: str
    is_dir: bool
    mode: int = 0o755
    content: bytes = b""
    children: dict[str, "VFSNode"] = field(default_factory=dict)


class VirtualFileSystem:
    """In-memory Virtual File System loaded from a physical directory."""

    def __init__(self) -> None:
        """Initialize an empty root VFS node."""
        self.root = VFSNode(name="", is_dir=True, mode=0o755)
        self.loaded_from: str | None = None

    def load_from_disk(self, physical_path: str) -> None:
        """Load directory tree from disk into memory without modifying it."""
        if not physical_path or not os.path.isdir(physical_path):
            raise FileNotFoundError(
                f"VFS source directory not found: {physical_path}"
            )
        self.root = VFSNode(name="", is_dir=True, mode=0o755)
        self.loaded_from = os.path.abspath(physical_path)
        self._scan_directory(physical_path, self.root)

    def _scan_directory(self, current_disk_path: str, node: VFSNode) -> None:
        """Recursively populate VFSNode tree from disk."""
        for entry in sorted(os.listdir(current_disk_path)):
            full_path = os.path.join(current_disk_path, entry)
            if os.path.isdir(full_path):
                child = VFSNode(name=entry, is_dir=True, mode=0o755)
                node.children[entry] = child
                self._scan_directory(full_path, child)
            elif os.path.isfile(full_path):
                with open(full_path, "rb") as file_obj:
                    data = file_obj.read()
                child = VFSNode(
                    name=entry, is_dir=False, mode=0o644, content=data
                )
                node.children[entry] = child

    def resolve_path(
        self, cwd: list[str], target_path: str
    ) -> tuple[VFSNode | None, list[str]]:
        """Resolve a relative or absolute VFS path to its node and parts."""
        parts = [] if target_path.startswith("/") else list(cwd)

        for token in target_path.split("/"):
            if not token or token == ".":
                continue
            if token == "..":
                if parts:
                    parts.pop()
            else:
                parts.append(token)

        node = self.root
        for part in parts:
            if not node.is_dir or part not in node.children:
                return None, parts
            node = node.children[part]
        return node, parts

    def count_nodes(self, node: VFSNode | None = None) -> tuple[int, int]:
        """Count total directories and files in memory."""
        current = node if node is not None else self.root
        dirs = 1 if current.is_dir else 0
        files = 0 if current.is_dir else 1
        for child in current.children.values():
            sub_dirs, sub_files = self.count_nodes(child)
            dirs += sub_dirs
            files += sub_files
        return dirs, files

    def get_size(self, node: VFSNode) -> int:
        """Calculate total byte size of a file or directory recursively."""
        if not node.is_dir:
            return len(node.content)
        total = 0
        for child in node.children.values():
            total += self.get_size(child)
        return total