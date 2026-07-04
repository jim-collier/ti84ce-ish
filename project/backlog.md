<!-- markdownlint-disable MD007 -- Unordered list indentation -->
<!-- markdownlint-disable MD010 -- No hard tabs -->
<!-- markdownlint-disable MD033 -- No inline html -->
<!-- markdownlint-disable MD055 -- Table pipe style [Expected: leading_and_trailing; Actual: leading_only; Missing trailing pipe] -->
<!-- markdownlint-disable MD041 -- First line in a file should be a top-level heading -->

<!-- TOC ignore:true -->
# Project backlog

This is a product backlog just for pre-v1.0.0 release. After that, bugs, features, and enhancements will be mananged in Github Issues, and/or [todo.md](../todo.md)

<!-- TOC ignore:true -->
## Table of contents
<!-- TOC -->

- [Conventions](#conventions)
- [First steps](#first-steps)
- [Backlog](#backlog)
	- [Bugs](#bugs)
	- [New features and enhancements](#new-features-and-enhancements)
	- [Deferred](#deferred)
	- [Canceled](#canceled)
- [Application name ideas](#application-name-ideas)

<!-- /TOC -->

## Conventions

In each section, items are listed approximately from newest to oldest.

| Icon | Status
| :--: | :--
| 🔘   | Not started
| 🛠️   | Started, and/or partially complete
| ✅   | Complete
| 🚫   | Canceled

## First steps

## Backlog

### Bugs

### New features and enhancements

- ✅ Local CI/CD script overhaul
	- Done: split into a generic engine plus per-project config, added quiet, message, and quick flags.
	- Done: publish can run hands-off with a supplied or auto commit message.
	- Verified: runs the tests, builds the executable, installs it locally, and refreshes the screenshots.
- ✅ Fuzz and security test suites
	- Done: added a stdlib-only fuzz sweep and a security suite that pins down the calculator whitelist.
	- Fixed: the calculator now rejects non-real results and boolean literals, both surfaced by the fuzzer.
	- Verified: full suite passes.
- ✅ Screenshot gallery
	- Done: headless capture of four use-cases, downsampled thumbnails, and a responsive gallery in the README.
	- Verified: thumbnails render and open the full-size originals.

### Deferred

### Canceled


## Application name ideas

