from datetime import datetime
import getpass
import re
import socket
import stat
from src.vfs import VFSNode, VirtualFileSystem

EXPECTED_CHMOD_ARGS = 2
MIN_CP_ARGS = 2
ROLE_SHIFTS = {"u": 6, "g": 3, "o": 0}
PERM_BITS = {"r": 4, "w": 2, "x": 1}


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


def _apply_symbolic_mode(current_mode: int, mode_str: str) -> int | None:
    """Apply symbolic chmod string (e.g. u+x, go-w, +r) to permission bits."""
    match = re.fullmatch(r"([ugoa]*)([+-=])([rwx]+)", mode_str)
    if not match:
        return None
    who_part, op_part, perm_part = match.groups()
    roles = who_part if who_part and "a" not in who_part else "ugo"
    mask = 0
    for role in roles:
        bits = sum(PERM_BITS[ch] for ch in perm_part)
        mask |= bits << ROLE_SHIFTS[role]

    if op_part == "+":
        return current_mode | mask
    if op_part == "-":
        return current_mode & ~mask
    clear_mask = sum(0o7 << ROLE_SHIFTS[role] for role in roles)
    return (current_mode & ~clear_mask) | mask


def cmd_chmod(
    vfs: VirtualFileSystem, cwd: list[str], args: list[str]
) -> tuple[bool, str]:
    """Change file or directory permissions in memory."""
    if len(args) != EXPECTED_CHMOD_ARGS:
        return False, "chmod: invalid arguments (usage: chmod <mode> <path>)\n"

    mode_str, target = args
    node, _ = vfs.resolve_path(cwd, target)
    if node is None:
        return False, f"chmod: {target}: No such file or directory\n"

    if re.fullmatch(r"[0-7]{3,4}", mode_str):
        node.mode = int(mode_str, 8)
        return True, ""

    new_mode = _apply_symbolic_mode(node.mode, mode_str)
    if new_mode is None:
        return False, f"chmod: invalid mode: '{mode_str}'\n"
    node.mode = new_mode
    return True, ""


def _resolve_parent(
    vfs: VirtualFileSystem, cwd: list[str], path_str: str
) -> tuple[VFSNode | None, str]:
    """Resolve parent directory node and target basename for a VFS path."""
    if "/" not in path_str:
        parent, _ = vfs.resolve_path(cwd, ".")
        return parent, path_str
    
    parent_path, _, basename = path_str.rpartition("/")
    parent_node, _ = vfs.resolve_path(cwd, parent_path if parent_path else "/")
    return parent_node, basename


def cmd_cp(
    vfs: VirtualFileSystem, cwd: list[str], args: list[str]
) -> tuple[bool, str]:
    """Copy files or directories inside the in-memory VFS."""
    recursive = "-r" in args or "-R" in args
    paths = [arg for arg in args if arg not in ("-r", "-R")]
    if len(paths) != MIN_CP_ARGS:
        return False, "cp: invalid arguments (usage: cp [-r] <src> <dst>)\n"

    src_path, dst_path = paths
    src_node, _ = vfs.resolve_path(cwd, src_path)
    if src_node is None:
        return False, f"cp: {src_path}: No such file or directory\n"
    if src_node.is_dir and not recursive:
        return False, f"cp: -r not specified; omitting directory '{src_path}'\n"

    # Check if destination exists as an existing directory
    dst_node, _ = vfs.resolve_path(cwd, dst_path)
    if dst_node is not None and dst_node.is_dir:
        dst_node.children[src_node.name] = vfs.clone_node(
            src_node, src_node.name
        )
        return True, ""

    # Otherwise, resolve parent and copy/rename to the new basename
    parent_node, new_name = _resolve_parent(vfs, cwd, dst_path)
    if parent_node is None or not parent_node.is_dir or not new_name:
        return False, f"cp: cannot create '{dst_path}': No such directory\n"
    parent_node.children[new_name] = vfs.clone_node(src_node, new_name)
    return True, ""