import os
import sys
from .tui import run_app

def check_os():
    if os.name != 'nt':
        print("Error: This tool is designed to run on Windows only.")
        sys.exit(1)

def main():
    check_os()
    run_app()

if __name__ == "__main__":
    main()
