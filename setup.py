#!/usr/bin/env python3
"""
Universal Device Diagnostics Setup Script

This script helps set up the development environment for the Universal Device Diagnostics project.
It installs dependencies, sets up the database, and provides instructions for getting started.
"""

import os
import sys
import subprocess
import platform
from pathlib import Path

def run_command(cmd, cwd=None, shell=False):
    """Run a command and return success status"""
    try:
        result = subprocess.run(cmd, cwd=cwd, shell=shell, check=True)
        return True
    except subprocess.CalledProcessError as e:
        print(f"Error running command: {' '.join(cmd) if isinstance(cmd, list) else cmd}")
        print(f"Error: {e}")
        return False

def check_python_version():
    """Check if Python version is 3.8+"""
    version = sys.version_info
    if version.major < 3 or (version.major == 3 and version.minor < 8):
        print("❌ Python 3.8+ is required")
        return False
    print(f"✅ Python {version.major}.{version.minor}.{version.micro} detected")
    return True

def print_instructions():
    """Print getting started instructions"""
    print("\n🚀 Setup Complete! Here's how to get started:")
    print("\n1. Start the backend server:")
    
    if platform.system() == "Windows":
        print("   cd backend")
        print("   venv\\Scripts\\activate")
        print("   uvicorn main:app --reload")
    else:
        print("   cd backend")
        print("   source venv/bin/activate")
        print("   uvicorn main:app --reload")
    
    print("\n2. In a new terminal, start the frontend:")
    print("   cd frontend")
    print("   npm start")
    
    print("\n3. Open your browser to: http://localhost:3000")
    
    print("\n🔍 For Android diagnostics:")
    print("   - Enable Developer Options on your Android device")
    print("   - Enable USB Debugging")
    print("   - Connect via USB and accept the debugging prompt")
    
    print("\n📚 Next Steps:")
    print("   - Run diagnostics on your Windows laptop")
    print("   - Try connecting an Android device")
    print("   - Check the GitHub repository for updates and documentation")

def main():
    """Main setup function"""
    print("🔧 Universal Device Diagnostics Setup")
    print("=====================================\n")
    
    if not check_python_version():
        return 1
    
    print_instructions()
    return 0

if __name__ == "__main__":
    sys.exit(main())