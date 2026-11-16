import argparse
import getpass
import os
import socket
import sys
import tkinter as tk
from tkinter import scrolledtext
from src import commands
from src.vfs import VirtualFileSystem


class ShellEmulator:
    """Graphical OS shell emulator with UNIX-like command execution."""

    def __init__(
        self,
        root: tk.Tk,
        vfs_path: str | None = None,
        script_path: str | None = None,
    ) -> None:
        """Initialize main window, load VFS into memory, and set up UI."""
        self.root = root
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.script_error = False
        self.vfs = VirtualFileSystem()
        self.cwd: list[str] = []

        user = getpass.getuser()
        host = socket.gethostname()
        self.root.title(f"Эмулятор [{user}@{host}]")
        self.root.geometry("700x450")

        self.create_widgets()
        self.init_vfs()

        if self.script_path:
            self.root.after(100, self.run_startup_script)

    def create_widgets(self) -> None:
        """Create and arrange graphical widgets in the window."""
        self.text_area = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, state="disabled", bg="black", fg="lime"
        )
        self.text_area.pack(expand=True, fill="both", padx=5, pady=5)

        self.entry = tk.Entry(
            self.root, bg="black", fg="lime", insertbackground="lime"
        )
        self.entry.pack(fill="x", padx=5, pady=5)
        self.entry.bind("<Return>", self.handle_command_event)
        self.entry.focus()

        self.print_output("Welcome to Shell Emulator. Type 'help' for info.\n")

    def init_vfs(self) -> None:
        """Load VFS from disk into memory and display startup config."""
        self.print_output("--- Configuration Parameters ---\n")
        self.print_output(f"VFS Path: {self.vfs_path}\n")
        self.print_output(f"Startup Script: {self.script_path}\n")
        if self.vfs_path:
            try:
                self.vfs.load_from_disk(self.vfs_path)
                dirs, files = self.vfs.count_nodes()
                self.print_output(
                    f"VFS loaded in memory ({dirs} dirs, {files} files).\n"
                )
            except FileNotFoundError as exc:
                self.print_output(f"VFS Error: {exc}\n")
        self.print_output("--------------------------------\n")
        if not self.script_path:
            self.print_prompt()

    def print_output(self, text: str) -> None:
        """Print text to the emulator terminal display."""
        self.text_area.configure(state="normal")
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)
        self.text_area.configure(state="disabled")

    def get_cwd_str(self) -> str:
        """Return formatted current working directory path in VFS."""
        return "/" + "/".join(self.cwd)

    def print_prompt(self) -> None:
        """Print the command line prompt with current VFS path."""
        user = getpass.getuser()
        host = socket.gethostname()
        path_str = "~" if not self.cwd else self.get_cwd_str()
        self.print_output(f"{user}@{host}:{path_str}$ ")

    def handle_command_event(self, event: tk.Event) -> None:
        """Handle user input events triggered by pressing Enter."""
        cmd_line = self.entry.get().strip()
        self.entry.delete(0, tk.END)
        self.print_output(f"{cmd_line}\n")
        self.execute_command(cmd_line)
        if cmd_line != "exit":
            self.print_prompt()

    def parse_command(self, line: str) -> list[str]:
        """Parse command line, expanding environment variables."""
        expanded = os.path.expandvars(line)
        return expanded.split()

    def dispatch_command(
        self, cmd: str, args: list[str]
    ) -> tuple[bool, str] | None:
        """Dispatch command name to corresponding handler function."""
        handlers = {
            "ls": lambda: commands.cmd_ls(self.vfs, self.cwd, args),
            "cd": lambda: commands.cmd_cd(self.vfs, self.cwd, args),
            "pwd": lambda: commands.cmd_pwd(self.cwd, args),
            "who": lambda: commands.cmd_who(args),
            "du": lambda: commands.cmd_du(self.vfs, self.cwd, args),
            "chmod": lambda: commands.cmd_chmod(self.vfs, self.cwd, args),
            "cp": lambda: commands.cmd_cp(self.vfs, self.cwd, args),
            "vfs-info": lambda: (True, self.get_vfs_info()),
            "help": lambda: (True, self.get_help_text()),
        }
        handler = handlers.get(cmd)
        return handler() if handler else None

    def execute_command(self, line: str) -> bool:
        """Execute parsed commands and return True if successful."""
        if not line:
            return True

        parts = self.parse_command(line)
        cmd, args = parts[0], parts[1:]

        if cmd == "exit":
            self.root.quit()
            return True

        result = self.dispatch_command(cmd, args)
        if result is not None:
            success, output = result
            if output:
                self.print_output(output)
            return success

        self.print_output(
            f"Error: unknown command or invalid arguments: {cmd}\n"
        )
        return False

    def get_vfs_info(self) -> str:
        """Return memory status string of the loaded VFS."""
        dirs, files = self.vfs.count_nodes()
        source = self.vfs.loaded_from or "Empty in-memory root"
        return f"VFS Source: {source}\nDirectories: {dirs}, Files: {files}\n"

    def run_startup_script(self) -> None:
        """Execute commands from startup script, stopping on first error."""
        if not self.script_path or not os.path.isfile(self.script_path):
            self.print_output(
                f"Script Error: File not found: {self.script_path}\n"
            )
            self.script_error = True
            self.print_prompt()
            return

        with open(self.script_path, "r", encoding="utf-8") as file_obj:
            for line_num, raw_line in enumerate(file_obj, start=1):
                line = raw_line.strip()
                if not line:
                    continue
                self.print_prompt()
                self.print_output(f"{line}\n")
                if not self.execute_command(line):
                    self.print_output(
                        f"Script halted at line {line_num} due to error.\n"
                    )
                    self.script_error = True
                    break
                if line == "exit":
                    return
        self.print_prompt()

    def get_help_text(self) -> str:
        """Return formatted list of all available commands."""
        return (
            "Available commands:\n"
            "  ls [-l] [path]       - List directory contents\n"
            "  cd [path]            - Change current working directory\n"
            "  pwd                  - Print current working directory\n"
            "  du [-s] [path]       - Estimate space usage in bytes\n"
            "  who                  - Show who is logged on\n"
            "  chmod <mode> <path>  - Change file or directory permissions\n"
            "  cp [-r] <src> <dst>  - Copy files or directories in memory\n"
            "  vfs-info             - Show in-memory VFS statistics\n"
            "  help                 - Show this help message\n"
            "  exit                 - Exit the emulator\n"
        )


def parse_cli_args(argv: list[str]) -> argparse.Namespace:
    """Parse command line arguments for VFS and startup script paths."""
    parser = argparse.ArgumentParser(description="OS Shell Emulator")
    parser.add_argument("--vfs", type=str, default=None, help="Path to VFS")
    parser.add_argument(
        "--script", type=str, default=None, help="Path to startup script"
    )
    return parser.parse_args(argv)


if __name__ == "__main__":
    args = parse_cli_args(sys.argv[1:])
    root = tk.Tk()
    app = ShellEmulator(root, vfs_path=args.vfs, script_path=args.script)
    root.mainloop()