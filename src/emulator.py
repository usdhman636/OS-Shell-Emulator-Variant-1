import argparse
import getpass
import os
import socket
import sys
import tkinter as tk
from tkinter import scrolledtext


class ShellEmulator:
    """Graphical OS shell emulator supporting CLI args and startup scripts."""

    def __init__(
        self,
        root: tk.Tk,
        vfs_path: str | None = None,
        script_path: str | None = None,
    ) -> None:
        """Initialize the main window, debug config, and UI components."""
        self.root = root
        self.vfs_path = vfs_path
        self.script_path = script_path
        self.script_error = False

        user = getpass.getuser()
        host = socket.gethostname()
        self.root.title(f"Эмулятор [{user}@{host}]")
        self.root.geometry("700x450")

        self.create_widgets()
        self.print_debug_config()

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

    def print_debug_config(self) -> None:
        """Display startup configuration parameters for debugging."""
        self.print_output("--- Configuration Parameters ---\n")
        self.print_output(f"VFS Path: {self.vfs_path}\n")
        self.print_output(f"Startup Script: {self.script_path}\n")
        self.print_output("--------------------------------\n")
        if not self.script_path:
            self.print_prompt()

    def print_output(self, text: str) -> None:
        """Print text to the emulator terminal display."""
        self.text_area.configure(state="normal")
        self.text_area.insert(tk.END, text)
        self.text_area.see(tk.END)
        self.text_area.configure(state="disabled")

    def print_prompt(self) -> None:
        """Print the command line prompt."""
        user = getpass.getuser()
        host = socket.gethostname()
        self.print_output(f"{user}@{host}:~$ ")

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

    def execute_command(self, line: str) -> bool:
        """Execute parsed commands and return True if successful."""
        if not line:
            return True

        parts = self.parse_command(line)
        cmd = parts[0]
        args = parts[1:]

        if cmd == "exit":
            self.root.quit()
            return True
        if cmd == "help":
            self.cmd_help()
            return True
        if cmd in ("ls", "cd"):
            self.print_output(f"Command: {cmd}, Arguments: {args}\n")
            return True

        self.print_output(
            f"Error: unknown command or invalid arguments: {cmd}\n"
        )
        return False

    def run_startup_script(self) -> None:
        """Execute commands from startup script, stopping on first error."""
        if not self.script_path or not os.path.isfile(self.script_path):
            self.print_output(
                f"Script Error: File not found: {self.script_path}\n"
            )
            self.script_error = True
            self.print_prompt()
            return

        with open(self.script_path, "r", encoding="utf-8") as file:
            for line_num, raw_line in enumerate(file, start=1):
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

    def cmd_help(self) -> None:
        """Display list of available commands and descriptions."""
        help_text = (
            "Available commands:\n"
            "  ls [args] - List directory contents (stub)\n"
            "  cd [args] - Change directory (stub)\n"
            "  help      - Show this help message\n"
            "  exit      - Exit the emulator\n"
        )
        self.print_output(help_text)


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