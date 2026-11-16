from datetime import datetime
import getpass
import socket
import stat
from src.vfs import VFSNode, VirtualFileSystem


def format_long_entry(node: VFSNode) -> str:
    """Format a single VFSNode in UNIX ls -l style."""
    file_type = "d" if node.is_dir else "-"
    perms = stat.filemode(node.mode)[1:]
    size = len(node.content) if not node.is_dir else 0
    return f"{file_type}{perms} 1 user group {size:>6} {node.name}"


def cmd_ls(
    vfs: VirtualFileSystem, cwd: list[str], args: list[str]
) -> tuple[bool, str]:
    """List directory contents or file info in the VFS."""
    long_fmt = "-l" in args
    targets = [arg for arg in args if arg != "-l"]
    target = targets[0] if targets else "."

    node, _ = vfs.resolve_path(cwd, target)
    if node is None:
        return False, f"ls: {target}: No such file or directory\n"

    if not node.is_dir:
        text = format_long_entry(node) if long_fmt else node.name
        return True, f"{text}\n"

    entries = sorted(node.children.values(), key=lambda item: item.name)
    if not entries:
        return True, ""
    if long_fmt:
        lines = [format_long_entry(item) for item in entries]
        return True, "\n".join(lines) + "\n"
    names = [
        f"{item.name}/" if item.is_dir else item.name for item in entries
    ]
    return True, "  ".join(names) + "\n"


def cmd_cd(
    vfs: VirtualFileSystem, cwd: list[str], args: list[str]
) -> tuple[bool, str]:
    """Change current working directory in the VFS."""
    target = args[0] if args else "/"
    node, resolved_parts = vfs.resolve_path(cwd, target)
    if node is None:
        return False, f"cd: {target}: No such file or directory\n"
    if not node.is_dir:
        return False, f"cd: {target}: Not a directory\n"
    cwd.clear()
    cwd.extend(resolved_parts)
    return True, ""


def cmd_pwd(cwd: list[str], args: list[str]) -> tuple[bool, str]:
    """Print current working directory path in the VFS."""
    if args:
        return False, "pwd: too many arguments\n"
    path_str = "/" + "/".join(cwd)
    return True, f"{path_str}\n"


def cmd_who(args: list[str]) -> tuple[bool, str]:
    """Display active emulator user session information."""
    if args:
        return False, "who: too many arguments\n"
    user = getpass.getuser()
    host = socket.gethostname()
    timestamp = datetime.now().strftime("%Y-%m-%d %H:%M")
    return True, f"{user:<12} pts/0        {timestamp} ({host})\n"


def _collect_du_lines(
    vfs: VirtualFileSystem, node: VFSNode, path_label: str
) -> list[str]:
    """Collect disk usage lines recursively for subdirectories."""
    lines: list[str] = []
    for name, child in sorted(node.children.items()):
        if child.is_dir:
            child_path = (
                f"/{name}" if path_label == "/" else f"{path_label}/{name}"
            )
            lines.extend(_collect_du_lines(vfs, child, child_path))
    size = vfs.get_size(node)
    lines.append(f"{size}\t{path_label}")
    return lines


def cmd_du(
    vfs: VirtualFileSystem, cwd: list[str], args: list[str]
) -> tuple[bool, str]:
    """Estimate file and directory space usage in bytes."""
    summary_only = "-s" in args
    targets = [arg for arg in args if arg != "-s"]
    target = targets[0] if targets else "."

    node, _ = vfs.resolve_path(cwd, target)
    if node is None:
        return False, f"du: {target}: No such file or directory\n"

    if summary_only or not node.is_dir:
        return True, f"{vfs.get_size(node)}\t{target}\n"

    lines = _collect_du_lines(vfs, node, target)
    return True, "\n".join(lines) + "\n"