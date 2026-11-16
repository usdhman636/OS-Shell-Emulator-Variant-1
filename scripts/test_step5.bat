@echo off
REM Ensure sample directories exist with required test files for cp and chmod
mkdir vfs_samples\deep\level1\level2\level3 2>nul
echo sample content 1 > vfs_samples\deep\file1.txt
echo sample content 2 > vfs_samples\deep\level1\level2\file2.txt
echo === Running Step 5: Additional Commands Test ===
python -m src.emulator --vfs vfs_samples/deep --script scripts/startup_modify_cmds.txt