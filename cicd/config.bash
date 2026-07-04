#!/bin/bash

#  shellcheck disable=2034  ## 'variable appears unused.' Config values are read by cicd.bash after sourcing.

##	Purpose:
##		- Project-specific CI/CD settings for the TI-84 CE+ calculator.
##		- To reuse this pipeline elsewhere, copy the whole cicd/ directory and edit THIS file
##		  (cicd.bash stays generic). All command arrays run from the source dir (github/).
##	History: At bottom of script.

##	Copyright © 2026 Jim Collier (ID: 1cv◂‡Vᛦ)
##	Licensed under The MIT License (MIT). Full text at:
##		https://mit-license.org/
##	SPDX-License-Identifier: MIT


## Guard: sourced only.
declare -i isSourced_cfg=0; [[ "${BASH_SOURCE[0]}" == "${0}" ]] || isSourced_cfg=1
((isSourced_cfg)) || { echo -e "\nError: $(basename "${BASH_SOURCE[0]}") is meant to be sourced from cicd.bash.\n"; exit 1; }


## Identity
APP_NAME="TI-84 CE+"
EXE_NAME="ti84ce"

## Regression tests (fast; always run).
TEST_CMD=(python3 -m unittest discover -s tests -v)

## Slow tests (fuzz sweeps at a much higher iteration count). Skipped under --quick.
## Left empty makes the slow stage a no-op.
SLOW_TEST_CMD=(env TI84_FUZZ_ITERS=8000 python3 -m unittest discover -s tests -p "test_fuzz*.py" -v)

## Release build: one self-contained executable. No cross targets (PyInstaller is per-OS).
BUILD_CMD=(python3 build.py)
BUILD_ARTIFACT="dist/${EXE_NAME}"

## Dogfood: copy the freshly built exe into the first existing dir here.
DOGFOOD_DESTS=(
	"${HOME}/synced/0-0/common/exec/util/linux/bin"
	"${HOME}/.local/bin"
	"/usr/local/sbin"
)

## Screenshot refresh hook (non-fatal, skipped under --quick).
SHOTS_HOOK="cicd/utility/screenshots.bash"

## Backup + publish to git (runs from the source dir).
GIT_PUBLISH=(cicd/utility/n8git_backup-and-publish)

## Fallback commit message used when -q is given without -m. Keep it terse.
PUBLISH_AUTO_MESSAGE="Updated"


##	History:
##		- 2026-07-04 JC: Created.
