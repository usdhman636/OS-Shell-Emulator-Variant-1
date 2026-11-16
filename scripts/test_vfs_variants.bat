@echo off
mkdir vfs_samples\minimal 2>nul
mkdir vfs_samples\flat 2>nul
echo hello > vfs_samples\flat\file1.txt
echo world > vfs_samples\flat\file2.txt
mkdir vfs_samples\deep\level1\level2\level3 2>nul
echo deep data > vfs_samples\deep\level1\level2\level3\secret.txt

echo 1. Testing minimal VFS...
python -m src.emulator --vfs vfs_samples/minimal --script scripts/startup_vfs_test.txt

echo 2. Testing flat VFS with multiple files...
python -m src.emulator --vfs vfs_samples/flat --script scripts/startup_vfs_test.txt

echo 3. Testing 3-level nested VFS and error handling...
python -m src.emulator --vfs vfs_samples/deep --script scripts/startup_vfs_test.txt