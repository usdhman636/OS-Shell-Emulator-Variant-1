# OS Shell Emulator - Variant 1

## General Description
A graphical user interface (GUI) shell emulator mimicking a UNIX-like operating system command line. Loads a directory from disk into an in-memory Virtual File System (VFS) and performs all navigation, inspection, and modification commands strictly in RAM without altering the physical disk.

## Functions and Settings
* **In-Memory VFS**: Loads a directory tree from `--vfs` into memory (`VFSNode` tree) with support for relative/absolute paths (`.`, `..`, `/`) and deep node cloning.
* **Command Line Arguments**:
  * `--vfs <path>`: Physical path to the source directory for the VFS.
  * `--script <path>`: Path to an emulator startup script (halts execution on the first error).
* **Environment Variables**: Automatically expands real OS environment variables (e.g., `$USERPROFILE`, `$HOME`).
* **Commands**:
  * `ls [-l] [path]`: List directory contents or file metadata (`-l` for permissions, size, and type).
  * `cd [path]`: Change current working directory in the VFS.
  * `pwd`: Print current working directory path.
  * `du [-s] [path]`: Estimate file and directory space usage in bytes (`-s` for summary).
  * `who`: Display current emulator user session information.
  * `chmod <mode> <path>`: Modify file or directory permissions in memory (octal e.g. `755` or symbolic e.g. `u+x`, `go-w`).
  * `cp [-r] <src> <dst>`: Copy files or directories (`-r` for recursive copy) strictly in memory.
  * `vfs-info`: Display loaded VFS source path, directory count, and file count in memory.
  * `help`: Display all available commands and their descriptions.
  * `exit`: Close the emulator application.

## Build and Test Commands
* **Run Emulator**: `make run`
* **Run Unit Tests**: `make test`
* **Clean Build Artifacts**: `make clean`

## Usage Examples
1. Launch interactively with a VFS directory:
   `python -m src.emulator --vfs vfs_samples/deep`
2. Run the Step 5 automated startup script testing `chmod`, `cp`, and error handling:
   `python -m src.emulator --vfs vfs_samples/deep --script scripts/startup_modify_cmds.txt`
3. Run the Windows batch script covering multiple VFS variants:
   `scripts\test_vfs_variants.bat`