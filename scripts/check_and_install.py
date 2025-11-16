#!/usr/bin/env python3
"""
Check for required packages and attempt installation
"""
import subprocess
import sys
import os

REQUIRED_PACKAGES = {
    'beautifulsoup4': 'bs4',
    'requests': 'requests',
    'pdfplumber': 'pdfplumber',
    'google-generativeai': 'google.generativeai',
    'python-dotenv': 'dotenv',
    'loguru': 'loguru',
    'lxml': 'lxml'
}

def check_package(import_name):
    """Check if a package can be imported"""
    try:
        __import__(import_name)
        return True
    except ImportError:
        return False

def install_package(package_name):
    """Attempt to install a package"""
    try:
        result = subprocess.run(
            [sys.executable, '-m', 'pip', 'install', '--user', package_name],
            capture_output=True,
            text=True,
            timeout=120
        )
        return result.returncode == 0
    except Exception as e:
        print(f"Error installing {package_name}: {e}")
        return False

def main():
    print("Checking required packages...")
    print("=" * 60)
    
    missing = []
    installed = []
    
    for package_name, import_name in REQUIRED_PACKAGES.items():
        if check_package(import_name):
            print(f"✓ {package_name} - Already installed")
            installed.append(package_name)
        else:
            print(f"✗ {package_name} - Missing")
            missing.append(package_name)
    
    if missing:
        print(f"\nAttempting to install {len(missing)} missing packages...")
        print("=" * 60)
        
        for package in missing:
            print(f"Installing {package}...", end=" ", flush=True)
            if install_package(package):
                print("✓ Success")
                installed.append(package)
            else:
                print("✗ Failed")
        
        # Re-check
        print("\nRe-checking packages...")
        still_missing = []
        for package_name, import_name in REQUIRED_PACKAGES.items():
            if not check_package(import_name):
                still_missing.append(package_name)
        
        if still_missing:
            print(f"\n⚠ Still missing: {', '.join(still_missing)}")
            print("\nPlease install manually:")
            print(f"python3 -m pip install --user {' '.join(still_missing)}")
            return False
        else:
            print("\n✓ All packages installed successfully!")
            return True
    else:
        print("\n✓ All packages are already installed!")
        return True

if __name__ == "__main__":
    success = main()
    sys.exit(0 if success else 1)


