import os
import tempfile
import tkinter as tk
import unittest
from src.emulator import ShellEmulator


class TestAdditionalCommands(unittest.TestCase):
    """Unit tests for in-memory chmod and cp commands."""

    def setUp(self) -> None:
        """Create temporary VFS directory and initialize emulator."""
        self.temp_dir = tempfile.TemporaryDirectory()
        base = self.temp_dir.name
        sub_dir = os.path.join(base, "level1", "level2")
        os.makedirs(sub_dir)
        with open(os.path.join(base, "file1.txt"), "wb") as file_a:
            file_a.write(b"hello")
        with open(os.path.join(sub_dir, "inner.txt"), "wb") as file_b:
            file_b.write(b"world")

        self.root = tk.Tk()
        self.emu = ShellEmulator(self.root, vfs_path=base)

    def tearDown(self) -> None:
        """Destroy GUI root and clean up temporary directory."""
        self.root.destroy()
        self.temp_dir.cleanup()

    def test_chmod_octal_and_symbolic(self) -> None:
        """Test octal and symbolic permission updates in memory."""
        self.assertTrue(self.emu.execute_command("chmod 750 file1.txt"))
        node, _ = self.emu.vfs.resolve_path([], "file1.txt")
        self.assertEqual(node.mode, 0o750)

        self.assertTrue(self.emu.execute_command("chmod o+r file1.txt"))
        self.assertEqual(node.mode, 0o754)
        self.assertFalse(self.emu.execute_command("chmod invalid file1.txt"))

    def test_cp_file_and_recursive_dir(self) -> None:
        """Test copying files and recursive directories in memory."""
        self.assertTrue(self.emu.execute_command("cp file1.txt file1_copy.txt"))
        copied_file, _ = self.emu.vfs.resolve_path([], "file1_copy.txt")
        self.assertIsNotNone(copied_file)
        self.assertEqual(copied_file.content, b"hello")

        self.assertFalse(self.emu.execute_command("cp level1 level1_backup_fail"))
        self.assertTrue(self.emu.execute_command("cp -r level1 level1_backup"))
        copied_inner, _ = self.emu.vfs.resolve_path(
            [], "level1_backup/level2/inner.txt"
        )
        self.assertIsNotNone(copied_inner)
        self.assertEqual(copied_inner.content, b"world")


if __name__ == "__main__":
    unittest.main()