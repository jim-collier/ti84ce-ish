<!-- markdownlint-disable MD007 -- Unordered list indentation -->
<!-- markdownlint-disable MD010 -- No hard tabs -->
<!-- markdownlint-disable MD041 -- First line in a file should be a top-level heading -->

<!-- TOC ignore:true -->
# Project backlog

<!-- TOC ignore:true -->
## Table of contents

<!-- TOC -->

- [Introduction](#introduction)
- [Issues](#issues)
- [Old format](#old-format)
	- [Bugs](#bugs)
	- [Features and enhancements](#features-and-enhancements)
	- [Done](#done)
		- [Done - Bugs](#done---bugs)
		- [Done - Features and enhancements](#done---features-and-enhancements)
	- [Deferred](#deferred)
	- [Canceled](#canceled)
- [Template](#template)

<!-- /TOC -->

## Introduction

Going forward, new issues in the new template at the bottom of this file, will go in the '## New format' section only. No more status emojis. Refer to '## Reference' for sort order. Issues in the old format (with status emojis) won't be refactored, but will continue to be worked until moved to closed, canceled, or deferred sections, and emojis updated. (Eventually this will all be moved to nano-git-db anyway. This new template is an intermediate effort to make issues going forward more structured and importable.)

This is a product backlog just for pre-v1.0.0 release. After that, bugs, features, and enhancements will be mananged in Github Issues, and/or [todo.md](../todo.md)

## Issues

- CICD reset: containers
	- ID: 2026102416331500
	- Type: Enhancement
	- Status: Queued
	- Priority [Feature|Enhancement] | Severity [Bug]: High
	- Opened: 20261024-163315
	- Opened by: JC
	- Requirements [Feature]:
		- Sweeping override, 2026-10-24: this supersedes any earlier decision on this project that conflicts with it.
		- Tests and the Linux build run by default in an image built from a pinned recipe in the repo, such as `cicd/container/`, with pinned Python, Tk, and PyInstaller.
		- A missing docker or an image that won't build falls back to the host with one line saying so, and never fails the run. `--no-container` runs on the host on purpose.
		- Screenshots and other checks that need a real desktop stay on the host.

- CICD reset: other hosts and VMs
	- ID: 2026102416331501
	- Type: Enhancement
	- Status: Queued
	- Needs external testing: Yes, on the Windows and macOS test boxes.
	- Priority [Feature|Enhancement] | Severity [Bug]: High
	- Opened: 20261024-163315
	- Opened by: JC
	- Requirements [Feature]:
		- Sweeping override, 2026-10-24: this supersedes any earlier decision on this project that conflicts with it.
		- The build script makes a native binary only on the OS it runs on, so the default run builds and tests the Windows and macOS binaries on those test boxes. Linux on arm64 too, if it's quick enough there. `--no-remote` skips them.
		- Windows goes to b29w first, and to vm925w only for GPU or timed work.
		- Each box is held through the shared host lock while it's in use. A VM is put back the way it was found, through the VM state helper.
		- A box that isn't there shows as SKIP with a warning, and the run goes on.
		- Each box gets a work folder for this project under its temp root.

- CICD reset: container cleanup
	- ID: 2026102416331502
	- Type: Enhancement
	- Status: Queued
	- Priority [Feature|Enhancement] | Severity [Bug]: High
	- Opened: 20261024-163315
	- Opened by: JC
	- Prereq IDs: 2026102416331500
	- Requirements [Feature]:
		- Sweeping override, 2026-10-24: this supersedes any earlier decision on this project that conflicts with it.
		- Every container, image, and volume the pipeline makes gets the `dev.project` and `dev.run` labels. Containers are named by project, run, and step.
		- Containers run with `--rm` unless `--keep-temp` is passed.
		- At the end of a run, on failure and Ctrl+C too, the run's containers are removed by label. Then the project's dangling images, and its older tags once a newer one passed, keeping the current tag and the one before.
		- Then `docker builder prune -f --filter until=168h`. Cache volumes are kept under 2 GB.
		- Nothing without this project's label is touched. No `docker rmi -f` and no `docker system prune`.

- CICD reset: CPU and priority
	- ID: 2026102416331503
	- Type: Enhancement
	- Status: Queued
	- Priority [Feature|Enhancement] | Severity [Bug]: High
	- Opened: 20261024-163315
	- Opened by: JC
	- Requirements [Feature]:
		- Sweeping override, 2026-10-24: this supersedes any earlier decision on this project that conflicts with it.
		- Build and test use at most half the CPUs, or a quarter on a busy box. Busy means the 1-minute load is over half the CPU count, checked at the start and before each step.
		- The fuzz sweep and any leak checks use a quarter, busy or not.
		- The counts are worked out in one place and passed to every tool that runs in parallel.
		- Every step runs under `nice -n 19` and `ionice -c 3`. Containers get `--cpus` and `--cpu-shares 256`.
		- Other hosts follow the same rules with their own CPU count and load. Windows runs at `BelowNormal`.

- CICD reset: standard flags
	- ID: 2026102416331504
	- Type: Enhancement
	- Status: Queued
	- Priority [Feature|Enhancement] | Severity [Bug]: High
	- Opened: 20261024-163315
	- Opened by: JC
	- Requirements [Feature]:
		- Sweeping override, 2026-10-24: this supersedes any earlier decision on this project that conflicts with it.
		- `-q`, `-m`, `--quick`, and the `--no-*` flags are in. What's left is below.
		- New flags: `--long` with `--slow` as another name, `--leakcheck`, `--no-leakcheck`, `--backlog-run-quick` with optional areas, `--backlog-run-full`, `--merge-gate`, `--no-container`, `--no-remote`, `--no-sync`, `--keep-temp`, and `--list`. `--gate` and `--ci` are other names for the quick backlog run and the merge gate.
		- A plain run takes no more than about an hour, and `--quick` about 10 minutes, with the release build still in it.
		- The backlog runs and the merge gate never dogfood, publish, commit, push, install, sync, or rewrite a tracked file, and never prompt.
		- A pre-push hook runs `--merge-gate` on a push to main. It skips the gate when the commits touch only docs and the other paths listed in one place.
		- No gate on other pushes. There's no dev branch yet.

- CICD reset: step output
	- ID: 2026102416331505
	- Type: Enhancement
	- Status: Queued
	- Priority [Feature|Enhancement] | Severity [Bug]: High
	- Opened: 20261024-163315
	- Opened by: JC
	- Requirements [Feature]:
		- Sweeping override, 2026-10-24: this supersedes any earlier decision on this project that conflicts with it.
		- Each step prints a 79-character rule, a `Starting` line, its output, and a `PASS` or `FAIL` line, in the shared format with a local timestamp to the hundredth and "Step N of M".
		- One blank line between steps, and one at the end.
		- Steps turned off aren't counted. The first section lists them with the flag or reason for each.
		- The headers have a timestamp and the step name now, with no count and no closing line.

- CICD reset: a test for every Done item
	- ID: 2026102416331506
	- Type: Enhancement
	- Status: Queued
	- Priority [Feature|Enhancement] | Severity [Bug]: High
	- Opened: 20261024-163315
	- Opened by: JC
	- Requirements [Feature]:
		- Sweeping override, 2026-10-24: this supersedes any earlier decision on this project that conflicts with it.
		- Every Done feature and bug gets a regression test in CI, where one makes sense, and names its test ID. Otherwise it says in a few words why it has none.
		- That covers the 3 Done items: the pipeline overhaul, the fuzz and security suites, and the screenshot gallery.

- CICD reset: test IDs
	- ID: 2026102416331507
	- Type: Enhancement
	- Status: Queued
	- Priority [Feature|Enhancement] | Severity [Bug]: High
	- Opened: 20261024-163315
	- Opened by: JC
	- Requirements [Feature]:
		- Sweeping override, 2026-10-24: this supersedes any earlier decision on this project that conflicts with it.
		- Every CI test gets a unique ID: its creation time in whole minutes since 2000-01-01 UTC, in lowercase Crockford base 32. Take the time from the test's first commit, or the nearest evidence. An ID never changes.
		- The run prints one `PASS`, `FAIL`, or `SKIP` line per regression and fuzz test, with its ID and name, in place of the unittest listing.

- CICD reset: temp files and safe removal
	- ID: 2026102416331508
	- Type: Enhancement
	- Status: Queued
	- Priority [Feature|Enhancement] | Severity [Bug]: Avg
	- Opened: 20261024-163315
	- Opened by: JC
	- Requirements [Feature]:
		- Sweeping override, 2026-10-24: this supersedes any earlier decision on this project that conflicts with it.
		- Each run makes its own folder under `${HOST_TEMP}/<project>/`, named by time and a counter, and points `TMPDIR`, `TEMP`, and `TMP` at it. The headless display helper's files go there too.
		- A trap removes it at the end, on failure and Ctrl+C too. `--keep-temp` keeps it and prints the path.
		- Each run also removes this project's stale run folders, older than 2 days with no live process from their `run.pid`.
		- Recursive removes go through the repo's own copy of the safe removal guard. There are none yet.

- CICD reset: version line
	- ID: 2026102416331509
	- Type: Enhancement
	- Status: Queued
	- Priority [Feature|Enhancement] | Severity [Bug]: Avg
	- Opened: 20261024-163315
	- Opened by: JC
	- Requirements [Feature]:
		- Sweeping override, 2026-10-24: this supersedes any earlier decision on this project that conflicts with it.
		- The program gets `--version` and an About window that show `<program name> v<version> build <build>`, then the copyright line. It has neither now.
		- The build number is the commit time in minutes since 2000, in lowercase Crockford base 32, so builds stay reproducible.
		- A non-release build adds its build date after the build number. Release builds leave it off.

- CICD reset: macOS runner
	- ID: 2026102416331510
	- Type: Enhancement
	- Status: Queued
	- Priority [Feature|Enhancement] | Severity [Bug]: Avg
	- Opened: 20261024-163315
	- Opened by: JC
	- Target OS: macOS
	- Requirements [Feature]:
		- Sweeping override, 2026-10-24: this supersedes any earlier decision on this project that conflicts with it.
		- A hosted workflow on GitHub's free arm64 macOS runner builds the app and runs the tests that need no window. The window checks run on the Mac test boxes.
		- Pick which flags start it, by how long it takes.

- CICD reset: CICD process gaps
	- ID: 2026102416331511
	- Type: Enhancement
	- Status: Queued
	- Priority [Feature|Enhancement] | Severity [Bug]: Avg
	- Opened: 20261024-163315
	- Opened by: JC
	- Requirements [Feature]:
		- Sweeping override, 2026-10-24: this supersedes any earlier decision on this project that conflicts with it.
		- What's left of the shared CICD rules after the other reset items:
			- No fetch and fast-forward before the build.
			- No lint stage for Python or bash, no lint output under `cicd/artifacts/lint/`, and no lint `--check` gate.
			- No dev-mode test run that fails on `ResourceWarning`, no memray or tracemalloc soak test, and no pip-audit.
			- No profiler stage or flame report.
			- No `.deb`, `.rpm`, or Windows installer, and no checksums file.
			- No pinned tool versions, PyInstaller included.
			- A continue prompt after the commit message prompt.
			- `cicd/test.bash` is a harness left over from another project, and nothing runs it.
			- No demo video or gif.
			- No end-of-run line saying what cleanup removed and freed.

## Old format

### Bugs

### Features and enhancements

### Done

#### Done - Bugs

#### Done - Features and enhancements

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

## Template

### Old format

- 🔘 Not started

- 🛠️ Started, and/or partially complete

- 🔬 Testing not started or finished

- ✋ Defer

- ✅ Complete

- 🚫 Canceled

### New format

- Notes:

	- Only use rows that you actually need or expect will be filled in. Always fill in the title, ID, Type, Status, Opened and Created by.

	- The ID is the local time to the hundredth of a second. Opened is when it was written down, which may differ. (Use a keyboard macro and possibly something like project 'zuid' to generate.)

	- Status values meaning: Testing means the fix is in and checks are running or still to run. Waiting on signoff means automated testing passed. Moot means something else changed that made it irrelevant. Canceled means it still applies but was decided against. Waiting for testing means the fix is in and waits on a long CI run or an outside test host. Can't reproduce means a real attempt to reproduce it failed.

	- As issues are worked, and statuses change, place them in correct sorting order within the list:
		- First by status: Waiting for answers, Waiting on signoff, Testing, Waiting for testing, Can't reproduce, Stalled, Started, Queued, Done, Deferred, Canceled, Moot
		- Then by severity|priority: Critical, High, Avg, Low
		- Then by type: Bugs, [not bugs together]

	- Rows marked [Bug] are for bugs only, and rows marked [Feature] for features and enhancements. Priority and Severity share one row and one scale. Priority is for a Feature or Enhancement, and Severity for a Bug. Children are not nested. They sit at the top level and point back with Parent ID.

Template:

- Title
	- ID: YYYYmmDDHHMMSSNN
	- Type: [Bug|Feature|Enhancement|Task]
	- Status: [Queued|Waiting for answers|Waiting on signoff|Waiting for testing|Started|Testing|Stalled|Can't reproduce|Moot|Canceled|Deferred|Done]
	- Needs local test suite run?:
	- Needs external testing:
	- Priority [Feature|Enhancement] | Severity [Bug]: [Critical|High|Avg|Low]
	- Opened:
	- Opened by:
	- Assigned to:
	- Parent ID:
	- Prereq IDs:
	- Related IDs:
	- Target OS:
	- Test environment:
	- Version and build:
	- Requirements  [Feature]:
		- Hierarchical bulleted list.
	- Steps to reproduce [Bug]:
		- …
	- Incorrect behavior [Bug]:
	- Expected behavior [Bug]:
	- Reproduced [Bug]: [No, or when, where and how]
	- Possible cause [Bug]:
	- Actual cause [Bug]:
		- …
	- Estimated effort: [High|Avg|Low]
	- Actual effort: [High|Avg|Low]
	- Progress log:
		- …
	- Decisions:
		- …
	- Actual fix [Bug]:
	- Branch:
	- Commit:
	- Test case: [Reason not applicable, or CI test case #]
	- Acceptance signoff:
	- Superseded by ID:
	- Closed:
