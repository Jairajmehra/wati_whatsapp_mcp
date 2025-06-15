#!/usr/bin/env python3
"""
Script to help with publishing the WATI MCP server to PyPI.
"""

import os
import subprocess
import sys
from pathlib import Path


def run_command(cmd, description):
    """Run a command and handle errors."""
    print(f"\n🔧 {description}...")
    try:
        result = subprocess.run(cmd, shell=True, check=True, capture_output=True, text=True)
        print(f"✅ {description} completed successfully")
        if result.stdout:
            print(result.stdout)
        return True
    except subprocess.CalledProcessError as e:
        print(f"❌ {description} failed:")
        print(e.stderr)
        return False


def main():
    """Main publishing workflow."""
    print("🚀 WATI MCP Server Publishing Script")
    print("=" * 40)
    
    # Change to project root directory
    project_root = Path(__file__).parent.parent
    os.chdir(project_root)
    
    # Check if we're in a git repository
    if not Path(".git").exists():
        print("⚠️  Warning: Not in a git repository. Consider initializing git.")
    
    # Install build dependencies
    if not run_command("pip install build twine", "Installing build dependencies"):
        return False
    
    # Clean previous builds
    if Path("dist").exists():
        run_command("rm -rf dist/", "Cleaning previous builds")
    
    if Path("build").exists():
        run_command("rm -rf build/", "Cleaning build directory")
    
    # Run tests
    print("\n🧪 Running tests...")
    if not run_command("python -m pytest tests/ -v", "Running tests"):
        print("⚠️  Tests failed. Consider fixing them before publishing.")
        response = input("Continue anyway? (y/N): ")
        if response.lower() != 'y':
            return False
    
    # Build the package
    if not run_command("python -m build", "Building package"):
        return False
    
    # Check the package
    if not run_command("twine check dist/*", "Checking package"):
        return False
    
    print("\n📦 Package built successfully!")
    print("Files created:")
    for file in Path("dist").glob("*"):
        print(f"  - {file}")
    
    # Ask user what to do next
    print("\n🎯 What would you like to do next?")
    print("1. Upload to Test PyPI (recommended for first time)")
    print("2. Upload to PyPI (production)")
    print("3. Exit (manual upload)")
    
    choice = input("Enter your choice (1-3): ").strip()
    
    if choice == "1":
        print("\n📤 Uploading to Test PyPI...")
        print("You'll need to enter your Test PyPI credentials.")
        if run_command("twine upload --repository testpypi dist/*", "Uploading to Test PyPI"):
            print("✅ Upload successful!")
            print("You can test install with:")
            print("pip install --index-url https://test.pypi.org/simple/ wati-mcp-server")
    
    elif choice == "2":
        print("\n📤 Uploading to PyPI...")
        print("You'll need to enter your PyPI credentials.")
        if run_command("twine upload dist/*", "Uploading to PyPI"):
            print("✅ Upload successful!")
            print("Your package is now available at:")
            print("https://pypi.org/project/wati-mcp-server/")
            print("Users can install it with:")
            print("pip install wati-mcp-server")
    
    elif choice == "3":
        print("\n📋 Manual upload instructions:")
        print("To upload to Test PyPI:")
        print("  twine upload --repository testpypi dist/*")
        print("To upload to PyPI:")
        print("  twine upload dist/*")
    
    else:
        print("Invalid choice. Exiting.")
        return False
    
    print("\n🎉 Publishing process completed!")
    return True


if __name__ == "__main__":
    try:
        success = main()
        sys.exit(0 if success else 1)
    except KeyboardInterrupt:
        print("\n\n⏹️  Publishing cancelled by user.")
        sys.exit(1)
    except Exception as e:
        print(f"\n❌ Unexpected error: {e}")
        sys.exit(1) 