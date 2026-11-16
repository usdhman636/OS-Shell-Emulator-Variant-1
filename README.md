# OS Shell Emulator - Variant 1

## General Description
A graphical user interface (GUI) shell emulator mimicking a UNIX-like operating system command line. Loads a physical directory into an in-memory Virtual File System (VFS) without modifying disk contents.

## Functions and Settings
* **In-Memory VFS**: Reads a directory tree from `--vfs` into RAM (`VFSNode` tree) and resolves relative/absolute paths (`.`, `..`, `/`).
* **Command Line Arguments**:
  * `--vfs <path>`: Physical path to the source directory for the VFS.
  * `--script <path>`: Path to an emulator startup script (halts on first error).
* **Environment Variables**: Expands real OS variables (e.g., `$USERPROFILE`, `$HOME`).
* **Commands**:
  * `ls [path]`: Validate VFS path (stub for full listing).
  * `cd [path]`: Validate VFS path (stub for directory change).
  * `vfs-info`: Display loaded VFS source path, directory count, and file count in memory.
  * `help`: Display available commands and descriptions.
  * `exit`: Close the emulator application.

## Build and Test Commands
* **Run Emulator**: `make run`
* **Run Tests**: `make test`
* **Clean Artifacts**: `make clean`

## Usage Examples
1. Run VFS variant tests on Windows (minimal, flat, and 3-level nested VFS):
   `scripts\test_vfs_variants.bat`
2. Launch interactively with a specific VFS directory:
   `python -m src.emulator --vfs vfs_samples/deep`