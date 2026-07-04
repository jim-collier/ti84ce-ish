<!-- markdownlint-disable MD007 -- Unordered list indentation -->
<!-- markdownlint-disable MD010 -- No hard tabs -->
<!-- markdownlint-disable MD033 -- No inline html -->
<!-- markdownlint-disable MD055 -- Table pipe style [Expected: leading_and_trailing; Actual: leading_only; Missing trailing pipe] -->
<!-- markdownlint-disable MD041 -- First line in a file should be a top-level heading -->
<div align="center">

[![made-with-python](https://img.shields.io/badge/Made%20with-Python-1f425f.svg)](https://www.python.org/)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Lifecycle: Stable](https://img.shields.io/badge/Lifecycle-Stable-brightgreen)
![Support](https://img.shields.io/badge/Support-Maintained-brightgreen)
![Status: Passing](https://img.shields.io/badge/Status-Passing-brightgreen)

</div>
<!--
![Go](https://img.shields.io/badge/Go-00ADD8?logo=go&logoColor=white)
[![!#/bin/bash](https://img.shields.io/badge/-%23!%2Fbin%2Fbash-1f425f.svg?logo=gnu-bash)](https://www.gnu.org/software/bash/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow.svg)](https://opensource.org/licenses/MIT)
![License: GPL v2](https://img.shields.io/badge/License-GPLv2-blue.svg)
![License: GPL v3](https://img.shields.io/badge/License-GPLv3-blue.svg)
![Lifecycle: Alpha](https://img.shields.io/badge/Lifecycle-Alpha-orange)
![Lifecycle: Beta](https://img.shields.io/badge/Lifecycle-Beta-yellow)
![Lifecycle: RC](https://img.shields.io/badge/Lifecycle-RC-blue)
![Lifecycle: Stable](https://img.shields.io/badge/Lifecycle-Stable-brightgreen)
![Lifecycle: Deprecated](https://img.shields.io/badge/Lifecycle-Deprecated-red)
![Status: Deprecated](https://img.shields.io/badge/Status-Deprecated-orange)
![Status: Archived](https://img.shields.io/badge/Status-Archived-lightgrey)
![Lifecycle: EOL](https://img.shields.io/badge/Lifecycle-EOL-lightgrey)
![Coverage](https://img.shields.io/badge/Coverage-25%25-red)
![Coverage](https://img.shields.io/badge/Coverage-50%25-orange)
![Coverage](https://img.shields.io/badge/Coverage-75%25-yellow)
![Coverage](https://img.shields.io/badge/Coverage-90%25-brightgreen)
![Status: Passing](https://img.shields.io/badge/Status-Passing-brightgreen)
![Status: Failing](https://img.shields.io/badge/Status-Failing-red)
-->

<!-- TOC ignore:true -->
# TI-84 CE+ — Scientific Calculator with Python

A plotting calculator with Python scripting support. Inspired by the TI 84 Plus CE color calculator

Cross-platform (Linux · Windows · macOS) desktop scientific calculator
styled after the **TI-84 Plus CE Python Edition**, with three modes:

| Mode | What it does |
|------|--------------|
| **CALC**   | Full scientific keypad — trig (DEG/RAD), logs, powers/roots, factorial, constants (π, e, τ, φ), `Ans` chaining, a `2nd` modifier, and a scrolling answer history. |
| **GRAPH**  | Plot up to three `Y=` functions of `X` on a Cartesian grid with adjustable window (Xmin/Xmax/Ymin/Ymax). |
| **PYTHON** | A real Python editor + console. Write code, press **▶ RUN** (or `F5` / `Ctrl+Enter`) and see stdout/stderr — just like the calculator's on-device Python app. |

## Why Python + Tkinter?

The calculator's headline feature is *Python programming*, so the host
language **is** the feature — code typed in PYTHON mode runs on the same
interpreter. Tkinter ships with CPython on all three platforms, so the app
has **zero third-party dependencies** and runs out of the box.

## Requirements

- Python **3.8+** with Tkinter (bundled with the standard python.org installers).
  - Debian/Ubuntu: `sudo apt install python3-tk`
  - Fedora: `sudo dnf install python3-tkinter`
  - macOS (Homebrew): `brew install python-tk`
  - Windows: use the official installer with the *tcl/tk* option checked.

## Installation

### Linux

~~~bash
~~~

### Windows

### macOS

## Or clone the repository and run the latest version

```bash

git clone git@github.com:jim-collier/ti84ce-ish.git
ct ti84ce-ish

# Linux / macOS:
python3 ti84ce.py

# Windows
python ti84ce.py

# Or as a module:
python3 -m ti84ce
```

## Run the tests

```bash
python3 -m unittest discover -s tests -v
```

The engine tests run **headless** (no display needed) and cover arithmetic, glyph normalisation (`×÷−√²³⁻¹`), DEG/RAD trig, logs, roots, `Ans` chaining, error handling, and that the calculator parser rejects unsafe input (attribute access, `__import__`, arbitrary calls).

## Safety model

- **CALC** mode never runs raw `eval`. Expressions are parsed to an AST and only whitelisted operators, functions and constants are evaluated, so typing `__import__('os')` is rejected as an error.
- **PYTHON** mode *deliberately* executes arbitrary Python (that is the feature) in a worker thread, with `math` pre-imported and stdout/stderr captured into the console.

## Project layout

```
ti84ce.py            cross-platform launcher (checks for Tkinter)
ti84ce/
  __init__.py        package exports + version
  __main__.py        `python -m ti84ce` entry point
  engine.py          safe AST-based scientific evaluator (GUI-free)
  app.py             Tkinter GUI: CALC / GRAPH / PYTHON modes
tests/
  test_engine.py     headless unit tests for the engine
```

## Build a single-file executable

A helper script bundles everything into one self-contained native binary
(no Python install needed to run it):

```bash
pip install pyinstaller     # one-time
python3 build.py            # Linux / macOS
python  build.py            # Windows
```

Output (PyInstaller builds for whichever OS you run it on):

| OS | Produced file |
|----|---------------|
| Linux   | `dist/ti84ce`     (~12 MB) |
| Windows | `dist/ti84ce.exe` |
| macOS   | `dist/ti84ce` (+ `dist/ti84ce.app`) |

Then just run the file directly — double-click it, or from a terminal:

```bash
./dist/ti84ce        # Linux / macOS
dist\ti84ce.exe      # Windows
```

> A single executable is inherently per-platform: run `build.py` on each OS
> you want a binary for. The build is reproducible from the bundled
> `ti84ce.py` + `ti84ce/` package.

## Keyboard shortcuts

- **CALC**: type directly; `Enter` evaluates.
- **GRAPH**: edit a `Y=` field and press `Enter` to re-plot.
- **PYTHON**: `F5` or `Ctrl+Enter` to run.

## Screenshots

<!-- SCREENSHOTS:START -->
<div align="center">
<a href="assets/screenshots/large/01-calc.png"><img src="assets/screenshots/small/01-calc.png" alt="Scientific calculator" title="Scientific calculator" width="23%"></a>
<a href="assets/screenshots/large/02-graph.png"><img src="assets/screenshots/small/02-graph.png" alt="Function graphing" title="Function graphing" width="23%"></a>
<a href="assets/screenshots/large/03-python.png"><img src="assets/screenshots/small/03-python.png" alt="Python editor and console" title="Python editor and console" width="23%"></a>
<a href="assets/screenshots/large/04-calc-2nd.png"><img src="assets/screenshots/small/04-calc-2nd.png" alt="2nd-function keypad" title="2nd-function keypad" width="23%"></a>
</div>
<!-- SCREENSHOTS:END -->

## Copyright and license

> Copyright © 2026 Jim Collier (ID: 1cv◂‡Vᛦ)<br />
> Licensed under the GPLv3 License. See [license.md](license.md).
