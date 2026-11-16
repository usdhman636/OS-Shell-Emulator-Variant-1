import os
import tempfile
import tkinter as tk
import unittest
from src.emulator import ShellEmulator


class TestBasicCommands(unittest.TestCase):
    """Unit tests for ls, cd, pwd, du, and who commands."""

    def setUp(self) -> None:
        """Create temporary 3-level VFS structure and emulator instance."""
        self.temp_dir = tempfile.TemporaryDirectory()
        base = self.temp_dir.name
        level2 = os.path.join(base, "dir1", "dir2")
        os.makedirs(level2)
        with open(os.path.join(base, "a.txt"), "wb") as file_a:
            file_a.write(b"12345")
        with open(os.path.join(level2, "b.txt"), "wb") as file_b:
            file_b.write(b"1234567890")

        self.root = tk.Tk()
        self.emu = ShellEmulator(self.root, vfs_path=base)

    def tearDown(self) -> None:
        """Destroy GUI root and clean up temporary directory."""
        self.root.destroy()
        self.temp_dir.cleanup()

    def test_cd_and_pwd(self) -> None:
        """Test directory navigation and pwd output."""
        self.assertTrue(self.emu.execute_command("cd dir1/dir2"))
        self.assertEqual(self.emu.get_cwd_str(), "/dir1/dir2")
        self.assertTrue(self.emu.execute_command("pwd"))
        output = self.emu.text_area.get("1.0", tk.END)
        self.assertIn("/dir1/dir2\n", output)

        self.assertTrue(self.emu.execute_command("cd .."))
        self.assertEqual(self.emu.get_cwd_str(), "/dir1")
        self.assertFalse(self.emu.execute_command("cd missing"))

    def test_ls_and_du_and_who(self) -> None:
        """Test ls, du, and who outputs on in-memory VFS."""
        self.assertTrue(self.emu.execute_command("ls -l"))
        self.assertTrue(self.emu.execute_command("du -s"))
        self.assertTrue(self.emu.execute_command("who"))
        output = self.emu.text_area.get("1.0", tk.END)
        self.assertIn("a.txt", output)
        self.assertIn("15\t.", output)
        self.assertIn("pts/0", output)


if __name__ == "__main__":
    unittest.main()