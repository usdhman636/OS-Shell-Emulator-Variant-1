# OS Shell Emulator - Variant 1

## General Description
A graphical user interface (GUI) shell emulator mimicking a UNIX-like operating system command line. Supports command-line configuration and automated startup script execution.

## Functions and Settings
* **Command Line Arguments**:
  * `--vfs <path>`: Physical path to the Virtual File System directory.
  * `--script <path>`: Path to an emulator startup script.
* **Startup Scripts**: Executes commands sequentially, echoing prompts, inputs, and outputs. Automatically halts execution upon encountering the first error.
* **Debug Output**: Displays configured `VFS Path` and `Startup Script` on launch.
* **Environment Variables**: Expands real OS variables (e.g., `$USERPROFILE`, `$HOME`).
* **Commands**:
  * `ls [args]`: List directory contents (stub).
  * `cd [args]`: Change directory (stub).
  * `help`: Display available commands and descriptions.
  * `exit`: Close the emulator application.

## Build and Test Commands
* **Run Emulator**: `make run`
* **Run Tests**: `make test`
* **Clean Artifacts**: `make clean`

## Usage Examples
1. Run with custom parameters:
   `python src/emulator.py --vfs ./my_vfs --script scripts/startup_valid.txt`
2. Run Windows batch test suite:
   `scripts\test_all_params.bat`