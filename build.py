#!/usr/bin/env python3
"""
Build a single self-contained executable of the TI-84 CE+ calculator.

Run this on each OS you want a binary for -- PyInstaller produces a native
executable for the platform it runs on:

    Linux    ->  dist/ti84ce
    Windows  ->  dist/ti84ce.exe
    macOS    ->  dist/ti84ce        (also dist/ti84ce.app)

Usage:
    python3 build.py            # builds the onefile executable
    pip install pyinstaller     # one-time, if not already installed
"""

import subprocess
import sys
from pathlib import Path

ROOT = Path(__file__).resolve().parent


def main() -> int:
    try:
        import PyInstaller  # noqa: F401
    except ImportError:
        print("PyInstaller is not installed.  Install it with:\n"
              "    pip install pyinstaller", file=sys.stderr)
        return 1

    cmd = [
        sys.executable, "-m", "PyInstaller",
        "--onefile",                 # single self-contained file
        "--windowed",                # no console window (GUI app)
        "--name", "ti84ce",
        "--noconfirm",               # overwrite a previous build
        "--clean",
        "--add-data", f"ti84ce{_sep()}ti84ce",  # bundle the package source
        str(ROOT / "ti84ce.py"),
    ]
    print("Running:", " ".join(cmd))
    result = subprocess.run(cmd, cwd=ROOT)
    if result.returncode == 0:
        out = ROOT / "dist"
        print(f"\nDone.  Executable is in: {out}")
    return result.returncode


def _sep() -> str:
    """PyInstaller --add-data uses ';' on Windows and ':' elsewhere."""
    return ";" if sys.platform.startswith("win") else ":"


if __name__ == "__main__":
    raise SystemExit(main())
