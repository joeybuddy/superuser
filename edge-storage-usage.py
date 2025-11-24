#!/usr/bin/env python3

"""
Script: edge-storage-usage.py
Description: Calculate Microsoft Edge browser storage usage on macOS
Usage: ./edge-storage-usage.py [username1] [username2] ...
       If no usernames provided, defaults to current user
"""

import os
import sys
import subprocess
import getpass
import platform
from pathlib import Path
from typing import Dict, Optional


# Byte conversion constants
KB = 1024
MB = 1024 * 1024
GB = 1024 * 1024 * 1024

# Formatting constants
LABEL_WIDTH = 30
SIZE_WIDTH = 15


# ANSI color codes
class Colors:
    RED = '\033[0;31m'
    GREEN = '\033[0;32m'
    YELLOW = '\033[1;33m'
    BLUE = '\033[0;34m'
    NC = '\033[0m'  # No Color


def format_bytes(bytes_size: int) -> str:
    """Format bytes to human-readable format."""
    if bytes_size < KB:
        return f"{bytes_size}B"
    elif bytes_size < MB:
        return f"{bytes_size / KB:.2f}KB"
    elif bytes_size < GB:
        return f"{bytes_size / MB:.2f}MB"
    else:
        return f"{bytes_size / GB:.2f}GB"


def get_dir_size(path: Path) -> int:
    """Calculate directory or file size in bytes."""
    if not path.exists():
        return 0
    
    if path.is_file():
        try:
            return path.stat().st_size
        except (OSError, PermissionError):
            return 0
    
    # For directories, calculate total size of all files
    total_size = 0
    try:
        for item in path.rglob('*'):
            if item.is_file():
                try:
                    total_size += item.stat().st_size
                except (OSError, PermissionError):
                    continue
    except (OSError, PermissionError):
        pass
    
    return total_size


def get_home_directory(username: str) -> Optional[Path]:
    """Get the home directory for a given username."""
    NFS_HOME_DIR_KEY = 'NFSHomeDirectory:'
    
    current_user = getpass.getuser()
    
    if username == current_user:
        return Path.home()
    
    # Try /Users/{username}
    home_dir = Path(f"/Users/{username}")
    if home_dir.exists() and home_dir.is_dir():
        return home_dir
    
    # Try dscl command to get home directory
    try:
        result = subprocess.run(
            ['dscl', '.', '-read', f'/Users/{username}', 'NFSHomeDirectory'],
            capture_output=True,
            text=True,
            check=False
        )
        if result.returncode == 0:
            for line in result.stdout.splitlines():
                if NFS_HOME_DIR_KEY in line:
                    path_str = line.split(NFS_HOME_DIR_KEY, 1)[1].strip()
                    home_dir = Path(path_str)
                    if home_dir.exists() and home_dir.is_dir():
                        return home_dir
    except Exception:
        pass
    
    return None


def calculate_edge_storage(username: str) -> bool:
    """Calculate Edge storage for a specific user."""
    home_dir = get_home_directory(username)
    
    if home_dir is None:
        print(f"{Colors.RED}✗ User '{username}' not found or home directory doesn't exist{Colors.NC}")
        return False
    
    print(f"\n{Colors.BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.NC}")
    print(f"{Colors.GREEN}User: {username}{Colors.NC}")
    print(f"{Colors.BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.NC}")
    
    # Define Edge-related directories
    edge_dirs: Dict[str, Path] = {
        "Application Support": home_dir / "Library/Application Support/Microsoft Edge",
        "Caches": home_dir / "Library/Caches/Microsoft Edge",
        "Cookies": home_dir / "Library/Cookies/com.microsoft.edgemac.binarycookies",
        "HTTPStorages": home_dir / "Library/HTTPStorages/com.microsoft.edgemac",
        "Preferences": home_dir / "Library/Preferences/com.microsoft.edgemac.plist",
        "Saved Application State": home_dir / "Library/Saved Application State/com.microsoft.edgemac.savedState",
        "WebKit": home_dir / "Library/WebKit/com.microsoft.edgemac",
    }
    
    total_size = 0
    found_any = False
    
    # Calculate size for each directory/file
    for label, path in edge_dirs.items():
        if path.exists():
            found_any = True
            size = get_dir_size(path)
            
            if size > 0:
                total_size += size
                print(f"  {label + ':':<{LABEL_WIDTH}} {format_bytes(size):>{SIZE_WIDTH}}")
    
    if not found_any:
        print(f"  {Colors.YELLOW}⚠ No Microsoft Edge data found for user '{username}'{Colors.NC}")
        return True
    
    print(f"{Colors.BLUE}──────────────────────────────────────────────────────────────{Colors.NC}")
    print(f"  {Colors.GREEN}{'TOTAL:':<{LABEL_WIDTH}} {format_bytes(total_size):>{SIZE_WIDTH}}{Colors.NC}")
    print(f"{Colors.BLUE}━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━━{Colors.NC}")
    
    return True


def main():
    """Main function."""
    # Check if running on macOS
    if platform.system() != "Darwin":
        print(f"{Colors.RED}Error: This script is designed for macOS only{Colors.NC}")
        sys.exit(1)
    
    print(f"{Colors.GREEN}╔════════════════════════════════════════════════════════════╗{Colors.NC}")
    print(f"{Colors.GREEN}║     Microsoft Edge Storage Usage Calculator for macOS     ║{Colors.NC}")
    print(f"{Colors.GREEN}╚════════════════════════════════════════════════════════════╝{Colors.NC}")
    
    # If no arguments provided, use current user
    if len(sys.argv) <= 1:
        usernames = [getpass.getuser()]
    else:
        usernames = sys.argv[1:]
    
    # Process each username
    for username in usernames:
        calculate_edge_storage(username)
    
    print()


if __name__ == "__main__":
    main()
