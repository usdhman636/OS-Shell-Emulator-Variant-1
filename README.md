# OS Shell Emulator - Variant 1

## General Description
A graphical user interface (GUI) shell emulator mimicking a UNIX-like operating system command line.

## Functions and Settings
* **GUI Window**: Title dynamically reflects real OS username and hostname.
* **Environment Variables**: Automatically expands real OS environment variables (e.g., `$HOME`).
* **Commands**:
  * `ls`: Stub command displaying name and arguments.
  * `cd`: Stub command displaying name and arguments.
  * `help`: Displays available commands and descriptions.
  * `exit`: Closes the emulator application.

## Build and Test Commands
* **Run Emulator**: `make run`
* **Run Tests**: `make test`
* **Clean Artifacts**: `make clean`

## Usage Examples
1. Launch the emulator using `make run`.
2. Type `help` to view available commands.
3. Type `ls /home/$USER` to test environment variable expansion.
4. Type `unknowncmd` to test error reporting.