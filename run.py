#!/usr/bin/env python3
"""
Launch script for the 3D game.
This script checks for dependencies and runs the game.
"""
import sys
import subprocess
import importlib.util


def check_module(module_name):
    """Check if a module is installed."""
    return importlib.util.find_spec(module_name) is not None


def install_requirements():
    """Install required packages from requirements.txt."""
    print("Installing requirements...")
    try:
        subprocess.check_call([sys.executable, "-m", "pip", "install", "-r", "requirements.txt"])
        print("Requirements installed successfully!")
        return True
    except subprocess.CalledProcessError:
        print("Failed to install requirements.")
        return False


def main():
    """Check dependencies and launch the game."""
    # Check if Ursina is installed
    if not check_module("ursina"):
        print("Ursina is not installed.")
        if not install_requirements():
            print("Please install required packages manually using:")
            print("pip install -r requirements.txt")
            sys.exit(1)
    
    print("Starting game...")
    try:
        import game
        game.main()
    except ImportError as e:
        print(f"Error importing game module: {e}")
        sys.exit(1)
    except Exception as e:
        print(f"Error running game: {e}")
        sys.exit(1)


if __name__ == "__main__":
    main() 