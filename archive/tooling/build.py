#!/usr/bin/env python3
"""
Build script for the vcgc package
"""

import subprocess
import sys
import os

def run_command(cmd, description):
    """Run a shell command and print its status"""
    print(f"\n🔧 {description}...")
    result = subprocess.run(cmd, shell=True, capture_output=True, text=True)
    
    if result.returncode == 0:
        print(f"✅ {description} successful")
        if result.stdout.strip():
            print(f"   Output: {result.stdout.strip()}")
        return True
    else:
        print(f"❌ {description} failed")
        print(f"   Error: {result.stderr.strip()}")
        return False

def main():
    """Main build process"""
    print("=== VCGC Package Build Script ===")
    
    # Change to the package directory
    os.chdir(os.path.dirname(os.path.abspath(__file__)))
    
    # Steps to build and test the package
    steps = [
        ("uv pip install -e .", "Installing package in development mode"),
        ("uv pip install pytest", "Installing test dependencies"), 
        (".venv/bin/python3 -m pytest tests/ -v", "Running tests"),
        (".venv/bin/python3 test_imports.py", "Testing imports"),
        (".venv/bin/python3 example_usage.py", "Running example"),
    ]
    
    success_count = 0
    for cmd, desc in steps:
        if run_command(cmd, desc):
            success_count += 1
        else:
            print(f"\n❌ Build failed at step: {desc}")
            sys.exit(1)
    
    print(f"\n🎉 Build completed successfully! ({success_count}/{len(steps)} steps)")
    print("\nThe vcgc package is ready to use!")
    print("\nQuick start:")
    print("  import vcgc")
    print("  network = vcgc.VCPNetwork()")
    print("  bf = vcgc.BooleanFunction()")
    print("  synth = vcgc.Synthesizer()")

if __name__ == "__main__":
    main()
