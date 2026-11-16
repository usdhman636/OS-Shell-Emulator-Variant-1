import os
import tempfile
import tkinter as tk
import unittest
from src.emulator import ShellEmulator, parse_cli_args


class TestShellEmulatorConfig(unittest.TestCase):
    """Unit tests for CLI arguments and startup script execution."""

    def setUp(self) -> None:
        """Set up test GUI root."""
        self.root = tk.Tk()

    def tearDown(self) -> None:
        """Destroy root window after test."""
        self.root.destroy()

    def test_cli_args_parsing(self) -> None:
        """Test parsing --vfs and --script arguments."""
        args = parse_cli_args(["--vfs", "C:\\vfs", "--script", "init.txt"])
        self.assertEqual(args.vfs, "C:\\vfs")
        self.assertEqual(args.script, "init.txt")

    def test_startup_script_stops_on_error(self) -> None:
        """Test that startup script halts upon encountering an invalid cmd."""
        with tempfile.NamedTemporaryFile(
            mode="w", delete=False, encoding="utf-8"
        ) as tmp:
            tmp.write("ls /valid\nbad_command\ncd /should_not_run\n")
            tmp_path = tmp.name

        try:
            emu = ShellEmulator(self.root, script_path=tmp_path)
            emu.run_startup_script()
            output = emu.text_area.get("1.0", tk.END)
            self.assertTrue(emu.script_error)
            self.assertIn("Script halted at line 2", output)
            self.assertNotIn("/should_not_run", output)
        finally:
            os.remove(tmp_path)


if __name__ == "__main__":
    unittest.main()