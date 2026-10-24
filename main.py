"""
Applied Physics 1 - Project 9: Main Launcher
Studying kinetic and potential energy of a particle moving under influence of conservative force.
"""

import sys
import os

# Ensure project directory is in python path
sys.path.insert(0, os.path.dirname(os.path.abspath(__file__)))


def main():
    if len(sys.argv) > 1 and sys.argv[1] in ["--cli", "-c", "--help", "-h"]:
        from cli import run_cli
        run_cli()
    else:
        try:
            from gui import launch_gui
            print("Starting Applied Physics 1 - Project 9 GUI...")
            launch_gui()
        except Exception as e:
            print(f"Failed to launch GUI ({e}). Falling back to interactive CLI...")
            from cli import run_cli
            run_cli()


if __name__ == "__main__":
    main()
