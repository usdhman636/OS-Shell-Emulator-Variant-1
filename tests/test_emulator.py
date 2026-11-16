import os
import tempfile
import tkinter as tk
import unittest
from src.emulator import ShellEmulator
from src.vfs import VirtualFileSystem


class TestVirtualFileSystem(unittest.TestCase):
    """Unit tests for in-memory Virtual File System operations."""

    def setUp(self) -> None:
        """Create temporary 3-level directory structure for VFS tests."""
        self.temp_dir = tempfile.TemporaryDirectory()
        base = self.temp_dir.name
        level3 = os.path.join(base, "dir1", "dir2", "dir3")
        os.makedirs(level3)
        with open(os.path.join(base, "root.txt"), "w", encoding="utf-8") as f:
            f.write("root content")
        with open(os.path.join(level3, "deep.txt"), "w", encoding="utf-8") as f:
            f.write("deep content")

    def tearDown(self) -> None:
        """Clean up temporary test directory."""
        self.temp_dir.cleanup()

    def test_load_multilevel_vfs_in_memory(self) -> None:
        """Test loading 3-level hierarchy into memory and resolving paths."""
        vfs = VirtualFileSystem()
        vfs.load_from_disk(self.temp_dir.name)
        dirs, files = vfs.count_nodes()
        self.assertEqual(dirs, 4)
        self.assertEqual(files, 2)

        node, parts = vfs.resolve_path([], "dir1/dir2/dir3/deep.txt")
        self.assertIsNotNone(node)
        self.assertEqual(parts, ["dir1", "dir2", "dir3", "deep.txt"])
        self.assertEqual(node.content, b"deep content")

    def test_emulator_vfs_error_handling(self) -> None:
        """Test emulator handles missing VFS paths gracefully."""
        root = tk.Tk()
        try:
            emu = ShellEmulator(root, vfs_path=self.temp_dir.name)
            self.assertTrue(emu.execute_command("ls dir1/dir2"))
            self.assertFalse(emu.execute_command("cd dir1/missing"))
        finally:
            root.destroy()


if __name__ == "__main__":
    unittest.main()