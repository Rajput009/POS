#!/usr/bin/env python3
"""
Verification script to check if the required components for the Pharmacy POS system are available.
"""

import sys
import importlib.util

def check_python_version():
    """Check if Python version is sufficient"""
    version = sys.version_info
    print(f"Python version: {version.major}.{version.minor}.{version.micro}")
    if version.major >= 3 and version.minor >= 6:
        print("✓ Python version is sufficient")
        return True
    else:
        print("✗ Python version is too old. Need Python 3.6 or higher")
        return False

def check_module(module_name, package_name=None):
    """Check if a module can be imported"""
    if package_name is None:
        package_name = module_name
    
    try:
        importlib.util.find_spec(module_name)
        print(f"✓ {package_name} is available")
        return True
    except ImportError:
        print(f"✗ {package_name} is not available")
        return False

def main():
    print("Verifying Pharmacy POS System Requirements...\n")
    
    # Check Python version
    python_ok = check_python_version()
    
    # Check required modules
    tkinter_ok = check_module("tkinter", "Tkinter")
    sqlite3_ok = check_module("sqlite3", "SQLite3")
    
    print("\n" + "="*50)
    if python_ok and tkinter_ok and sqlite3_ok:
        print("✓ All requirements are met. You can run the Pharmacy POS system!")
        print("\nTo run the application, execute:")
        print("  python main.py")
        print("\nOr on Windows:")
        print("  run.bat")
    else:
        print("✗ Some requirements are missing. Please install the missing components.")
    
    return python_ok and tkinter_ok and sqlite3_ok

if __name__ == "__main__":
    main()