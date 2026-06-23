#!/usr/bin/env python3
"""
Cross-platform launcher for the TI-84 CE+ scientific calculator.

Just run:  python3 ti84ce.py   (Linux/macOS)
       or  python ti84ce.py     (Windows)

Requires only the Python standard library (Tkinter ships with CPython).
"""

import sys


def _check_tkinter() -> None:
    try:
        import tkinter  # noqa: F401
    except ImportError:
        sys.stderr.write(
            "Tkinter is not available in this Python install.\n"
            "  Debian/Ubuntu : sudo apt install python3-tk\n"
            "  Fedora        : sudo dnf install python3-tkinter\n"
            "  macOS (brew)  : brew install python-tk\n"
            "  Windows       : reinstall Python with the 'tcl/tk' option checked\n"
        )
        sys.exit(1)


if __name__ == "__main__":
    _check_tkinter()
    from ti84ce.app import main
    main()
