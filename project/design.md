<!-- markdownlint-disable MD007 -- Unordered list indentation -->
<!-- markdownlint-disable MD010 -- No hard tabs -->
<!-- markdownlint-disable MD033 -- No inline html -->
<!-- markdownlint-disable MD055 -- Table pipe style [Expected: leading_and_trailing; Actual: leading_only; Missing trailing pipe] -->
<!-- markdownlint-disable MD041 -- First line in a file should be a top-level heading -->

<!-- TOC ignore:true -->
# Project design

<!-- TOC ignore:true -->
## Table of contents
<!-- TOC -->

- [Goal](#goal)
- [Architecture](#architecture)
	- [Language and stack](#language-and-stack)
	- [Logical code organization](#logical-code-organization)
	- [API](#api)

<!-- /TOC -->

## Goal

A cross-platform desktop calculator in the spirit of the TI-84 Plus CE Python Edition. Three modes in one window: a scientific calculator, a function grapher, and a real Python editor with a console.

## Architecture

### Language and stack

Python with Tkinter, standard library only, so it runs out of the box on Linux, Windows, and macOS with no third-party packages. A single-file executable is produced per platform with PyInstaller.

### Logical code organization

The evaluation engine is separate from the interface. The engine parses and evaluates calculator expressions with no GUI, so it can be tested on its own. The interface hosts the three mode panels and shares one engine instance.

### API

The engine exposes evaluation entry points for a full expression, for evaluation without storing the last answer, and for evaluating a function at a given X. Calculator mode is locked to a whitelist of numeric operators, math functions, and constants. Python mode runs arbitrary code by design.
