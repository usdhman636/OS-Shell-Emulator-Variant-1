# OS Shell Emulator - Variant 1

## General Description
A graphical user interface (GUI) shell emulator mimicking a UNIX-like operating system command line. Operates entirely in memory over a Virtual File System (VFS) loaded from disk.

## Functions and Settings
* **In-Memory VFS**: Loads a directory tree from `--vfs` into RAM without modifying source files on disk.
* **Command Line Arguments**:
  * `--vfs <path>`: Physical path to the source directory for the VFS.
  * `--script <path>`: Path to an emulator startup script (halts on first error).
* **Environment Variables**: Expands real OS variables (e.g., `$USERPROFILE`, `$HOME`).
* **Commands**:
  * `ls [-l] [path]`: List directory contents (supports `-l` long format).
  * `cd [path]`: Change current working directory in VFS.
  * `pwd`: Print current working directory path.
  * `du [-s] [path]`: Estimate file and directory space usage in bytes (`-s` for summary).
  * `who`: Display current emulator user session information.
  * `vfs-info`: Display loaded VFS source path and node counts.
  * `help`: Display available commands and descriptions.
  * `exit`: Close the emulator application.

## Build and Test Commands
* **Run Emulator**: `make run`
* **Run Tests**: `make test`
* **Clean Artifacts**: `make clean`

## Usage Examples
1. Run with the Step 4 test script:
   `python -m src.emulator --vfs vfs_samples/deep --script scripts/startup_basic_cmds.txt`
2. Run unit tests:
   `make test`