import unittest
import tkinter as tk
from src.emulator import ShellEmulator


class TestShellEmulator(unittest.TestCase):
    """Unit tests for ShellEmulator core logic."""

    def setUp(self) -> None:
        """Set up test GUI root and emulator instance."""
        self.root = tk.Tk()
        self.emulator = ShellEmulator(self.root)

    def tearDown(self) -> None:
        """Destroy root window after test."""
        self.root.destroy()

    def test_parse_command_env(self) -> None:
        """Test environment variable expansion in parser."""
        import os
        os.environ["TEST_VAR"] = "hello_world"
        parsed = self.emulator.parse_command("echo $TEST_VAR")
        self.assertEqual(parsed, ["echo", "hello_world"])


if __name__ == "__main__":
    unittest.main()