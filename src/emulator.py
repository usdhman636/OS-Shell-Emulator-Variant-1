import getpass
import os
import socket
import tkinter as tk
from tkinter import scrolledtext


class ShellEmulator:
    """Graphical OS shell emulator implementing a basic REPL."""

    def __init__(self, root: tk.Tk) -> None:
        """Initialize the main window and UI components."""
        self.root = root
        user = getpass.getuser()
        host = socket.gethostname()
        self.root.title(f"Эмулятор [{user}@{host}]")
        self.root.geometry("700x450")

        self.history: list[str] = []
        self.create_widgets()

    def create_widgets(self) -> None:
        """Create and arrange graphical widgets in the window."""
        self.text_area = scrolledtext.ScrolledText(
            self.root, wrap=tk.WORD, state="disabled", bg="black", fg="lime"
        )
        self.text_area.pack(expand=True, fill="both", padx=5, pady=5)

        self.entry = tk.Entry(self.root, bg="black", fg="lime", insertbackground="lime")
        self.entry.pack(fill="x", padx=5, pady=5)
        self.entry.bind("<Return>", self.handle_command_event)
        self.entry.focus()

        self.print_output("Welcome to Shell Emulator. Type 'help' for commands.\n")
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
        parts = expanded.split()
        return parts

    def execute_command(self, line: str) -> None:
        """Execute parsed commands or report errors."""
        if not line:
            return

        parts = self.parse_command(line)
        cmd = parts[0]
        args = parts[1:]

        if cmd == "exit":
            self.root.quit()
        elif cmd == "help":
            self.cmd_help()
        elif cmd in ("ls", "cd"):
            self.print_output(
                f"Command: {cmd}, Arguments: {args}\n"
            )
        else:
            self.print_output(
                f"Error: unknown command or invalid arguments: {cmd}\n"
            )

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


if __name__ == "__main__":
    root = tk.Tk()
    app = ShellEmulator(root)
    root.mainloop()