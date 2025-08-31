#!/usr/bin/env python3
"""
Script to start the Pharmacy POS application with proper error handling and guidance.
"""

import sys
import os
import subprocess

def check_python():
    """Check if Python is available"""
    try:
        result = subprocess.run([sys.executable, "--version"], 
                              capture_output=True, text=True, timeout=10)
        print(f"✓ {result.stdout.strip()}")
        return True
    except Exception as e:
        print(f"✗ Python not found or not working properly: {e}")
        return False

def check_tkinter():
    """Check if Tkinter is available"""
    try:
        import tkinter as tk
        print("✓ Tkinter is available")
        return True
    except ImportError:
        print("✗ Tkinter is not available")
        return False

def check_sqlite():
    """Check if SQLite is available"""
    try:
        import sqlite3
        print("✓ SQLite is available")
        return True
    except ImportError:
        print("✗ SQLite is not available")
        return False

def run_application():
    """Run the main application"""
    try:
        # Change to the script's directory
        script_dir = os.path.dirname(os.path.abspath(__file__))
        os.chdir(script_dir)
        
        # Import and run the main application
        import main
        print("✓ Pharmacy POS application started successfully!")
        return True
    except Exception as e:
        print(f"✗ Failed to start application: {e}")
        return False

def main():
    print("Pharmacy POS System - Startup Script")
    print("=" * 40)
    
    # Check requirements
    print("\nChecking requirements:")
    requirements_met = (
        check_python() and 
        check_tkinter() and 
        check_sqlite()
    )
    
    if not requirements_met:
        print("\n⚠️  Some requirements are missing!")
        print("Please ensure you have Python 3.6+ with Tkinter installed.")
        return 1
    
    print("\n✓ All requirements are met!")
    
    # Show instructions
    print("\nStarting Pharmacy POS application...")
    print("The application window should appear shortly.")
    print("Use the following credentials to log in:")
    print("  Username: admin")
    print("  Password: admin123")
    
    # Run the application
    if run_application():
        print("\n✅ Application is running!")
        return 0
    else:
        print("\n❌ Failed to start the application.")
        return 1

if __name__ == "__main__":
    sys.exit(main())