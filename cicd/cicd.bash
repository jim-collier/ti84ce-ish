#!/bin/bash
#  shellcheck disable=1091  ## 'source is valid here, but shellcheck doesn't know the path to it.'
#  shellcheck disable=2001  ## 'See if you can use ${variable//search/replace} instead.' Complains about good uses of sed.
#  shellcheck disable=2016  ## 'Expressions don't expand in single quotes, use double quotes for that.' I know, and I often want an explicit '$'.
#  shellcheck disable=2034  ## 'variable appears unused.' Complains about valid use of variable indirection (e.g. later use of local -n var=$1)
#  shellcheck disable=2046  ## 'Quote to prevent word-splitting.' (OK for integers.)
#  shellcheck disable=2086  ## 'Double quote to prevent globbing and word splitting.' (OK for integers.)
#  shellcheck disable=2119  ## 'Use foo "$@" if function's $1 should mean script's $1.' Confusing and inapplicable.
#  shellcheck disable=2120  ## 'Foo references arguments, but none are ever passed.' Valid function argument overloading.
#  shellcheck disable=2155  ## 'Declare and assign separately to avoid masking return values.' Cumbersome and unnecessary.
#  shellcheck disable=2181  ## 'Check exit code directly, not indirectly with $?.'
#  shellcheck disable=2317  ## 'Can't reach.' (I.e. an 'exit' is used for debugging - and makes an unusable visual mess.)

##	Purpose: Local CI/CD wrapper for a Python project. Runs tests, builds the single-file
##	         executable, dogfoods it locally, refreshes screenshots, then backs up and publishes.
##	         Generic engine; per-project settings live in config.bash.
##	Syntax:  cicd/cicd.bash [options]
##	         -q, --quiet          run unattended (no prompt); auto commit message unless -m given
##	         -m, --message MSG    hands-off publish with this commit message (also --msg, -m=MSG)
##	         --quick              skip the slow stages (release build + screenshots + slow tests)
##	         --no-test            skip the regression tests
##	         --no-build           skip the release build (and dogfood)
##	         --no-dogfood         skip installing the release locally
##	         --no-shots           skip the screenshot refresh
##	         --no-publish         skip the git backup + publish stage
##	         -h, --help  /  -v, --version
##	History: At bottom of this file.

##	Copyright © 2026 Jim Collier (ID: 1cv◂‡Vᛦ)
##	Licensed under The MIT License (MIT). Full text at:
##		https://mit-license.org/
##	SPDX-License-Identifier: MIT


#•••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
## Constants
if [[ -z "${doQuietly+x}" ]]; then
	declare  -i doQuietly=0
	declare  -i doPromptToContinue=1
	declare  -i doQuick=0
	declare     cli_message=""
	declare  -i doTest=1  doBuild=1  doDogfood=1  doShots=1  doPublish=1
	declare -r  thisVersion="1.0.0"
	declare -r  thisCopyrightYear="2026"
	declare -r  thisAuthor="Jim Collier"
	declare  -i wasShown_Version=0  wasShown_Copyright=0  wasShown_About=0  wasShown_Syntax=0
	## Full-width section rule for runtime output (leading blank line printed by fSection).
	declare -r  _sectionBar="•••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••"
fi


## Version, copyright, about, syntax (fEcho-based; minified but not obfuscated)
fVersion(){ { ((doQuietly)) || ((wasShown_Version)); } && return; wasShown_Version=1;
	fEcho_Clean "${meName} v${thisVersion}" ;:;}

fCopyright(){ { ((doQuietly)) || ((wasShown_Copyright)); } && return; wasShown_Copyright=1;
	fEcho_Clean ""
	fEcho_Clean "${meName}, Copyright © ${thisCopyrightYear} ${thisAuthor}."
	fEcho_Clean "Licensed under The MIT License (MIT). Full text at:"
	fEcho_Clean "  https://mit-license.org/"
	fEcho_Clean "No warranty."
	fEcho_Clean "" ;:;}

fAbout(){ { ((doQuietly)) || ((wasShown_About)); } && return; wasShown_About=1;
	fEcho_Clean ""
	fEcho_Clean "Local CI/CD for ${APP_NAME}:"
	fEcho_Clean "  • Run the regression tests. If they pass:"
	fEcho_Clean "  • Build the single-file executable. If it builds:"
	fEcho_Clean "  • Install it locally for dogfood."
	fEcho_Clean "  • Refresh the README screenshots."
	fEcho_Clean "  • Back up and publish to git."
	fEcho_Clean "" ;:;}

fSyntax(){ { ((doQuietly)) || ((wasShown_Syntax)); } && return; wasShown_Syntax=1;
	fEcho_Clean ""
	fEcho_Clean "Syntax: ${meName} [options]"
	fEcho_Clean "  -q, --quiet        Run unattended (no prompt). Auto commit message unless -m given."
	fEcho_Clean "  -m, --message MSG  Hands-off publish with this commit message (also --msg, -m=MSG)."
	fEcho_Clean "  --quick            Skip the slow stages (release build + screenshots + slow tests)."
	fEcho_Clean "  --no-test | --no-build | --no-dogfood | --no-shots | --no-publish"
	fEcho_Clean "  -h, --help  /  -v, --version"
	fEcho_Clean "" ;:;}

## Letterbox section header: blank line, the bullet rule, then a bracketed title.
fSection(){ fEcho_Clean ""; fEcho_Clean "${_sectionBar}"; fEcho "${1:-}"; }


#•••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
## Argument parsing
fParseCliArgs(){
	while (($#)); do case "$1" in
		-q|--quiet)          doQuietly=1;                        shift ;;
		--quick)             doQuick=1;                          shift ;;
		--no-test)           doTest=0;                           shift ;;
		--no-build)          doBuild=0;                          shift ;;
		--no-dogfood)        doDogfood=0;                        shift ;;
		--no-shots)          doShots=0;                          shift ;;
		--no-publish)        doPublish=0;                        shift ;;
		-m=*|--message=*|--msg=*)  cli_message="${1#*=}";        shift ;;
		-m|--message|--msg)  cli_message="${2-}"; shift; (($#)) && shift ;;
		-h|--help)           fCopyright; fAbout; fSyntax; exit 0 ;;
		-v|--version)        fVersion; exit 0 ;;
		*) fThrowError "Unknown option: '$1' (try --help)."; exit 2 ;;
	esac; done ;:;}


#•••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
fMain(){

	fParseCliArgs "${@}"

	## Validate dependencies
	fMustBeInPath python3
	fMustBeInPath git

	## --quick disables the slow stages.
	((doQuick)) && { doShots=0; }

	## Resolve the git automation script and screenshot hook (relative to source dir).
	local -r gitPublish="${GIT_PUBLISH[0]}"
	[[ -x "${gitPublish}" ]]  ||  fThrowError "Git automation script not found or not executable: '${gitPublish}'."

	## Commit message: -m wins, then the auto message when running quiet, else prompt later.
	local publishMsg=""
	if   [[ -n "${cli_message}"   ]]; then publishMsg="${cli_message}"
	elif ((doQuietly));              then publishMsg="${PUBLISH_AUTO_MESSAGE:-Updated}"
	fi

	## Preflight (skipped when quiet): show the plan, capture a message, confirm.
	if ((! doQuietly)); then
		fCopyright
		fAbout
		fEcho_Clean "Tests ...............: $( ((doTest)) && echo "${TEST_CMD[*]}" || echo "(skipped)" )"
		fEcho_Clean "Release build .......: $( { ((doBuild)) && ((! doQuick)); } && echo "${BUILD_CMD[*]} -> ${BUILD_ARTIFACT}" || echo "(skipped)" )"
		fEcho_Clean "Dogfood .............: $( ((doDogfood)) && echo "first of: ${DOGFOOD_DESTS[*]}" || echo "(skipped)" )"
		fEcho_Clean "Screenshots .........: $( { ((doShots)) && [[ -x "${SHOTS_HOOK}" ]]; } && echo "${SHOTS_HOOK}" || echo "(skipped)" )"
		fEcho_Clean "Publish .............: $( ((doPublish)) && echo "${gitPublish}" || echo "(skipped)" )"
		fEcho_Clean
		## Capture the commit message up front so the run can finish unattended.
		if ((doPublish)) && [[ -z "${publishMsg}" ]]; then
			read -r -p "Commit message (blank = editor; Ctrl+C aborts): " publishMsg
			fEcho_ResetBlankCounter
		fi
		fIntroPromptToContinue  ""  ||  return 1
		fEcho_Clean
	fi

	####
	#### MAKEITSO
	####

	## Stage: regression tests.
	if ((doTest)); then
		fSection "$(date "+%Y%m%d-%H%M%S") Tests"
		"${TEST_CMD[@]}"
		if ((! doQuick)) && ((${#SLOW_TEST_CMD[@]})); then
			fSection "$(date "+%Y%m%d-%H%M%S") Slow tests (fuzz + security)"
			"${SLOW_TEST_CMD[@]}"
		fi
		fEcho_ResetBlankCounter
	fi

	## Stage: release build.
	local -i builtOk=0
	if ((doBuild)) && ((! doQuick)); then
		fSection "$(date "+%Y%m%d-%H%M%S") Release build"
		"${BUILD_CMD[@]}"
		[[ -f "${BUILD_ARTIFACT}" ]]  ||  fThrowError "Release artifact missing: '${BUILD_ARTIFACT}'."
		builtOk=1
		fEcho "Built: ${BUILD_ARTIFACT} ($(du -h "${BUILD_ARTIFACT}" | cut -f1))"
	elif ((doBuild)) && ((doQuick)); then
		fSection "Release build"; fEcho_Clean "  skipped (--quick)"
	fi

	## Stage: dogfood (only if we have a fresh artifact).
	if ((doDogfood)) && ((builtOk)); then
		fSection "$(date "+%Y%m%d-%H%M%S") Dogfood"
		local installed=0 nextPath
		for nextPath in "${DOGFOOD_DESTS[@]}"; do
			if [[ -d "${nextPath}" ]]; then
				cp -f "${BUILD_ARTIFACT}"  "${nextPath%%/}/${EXE_NAME}"
				chmod +x "${nextPath%%/}/${EXE_NAME}"
				fEcho "Installed -> ${nextPath%%/}/${EXE_NAME}"
				installed=1
				break
			fi
		done
		((installed)) || fEcho "WARNING: no dogfood dir exists (${DOGFOOD_DESTS[*]}); skipping."
	fi

	## Stage: screenshots (non-fatal - a render miss must never abort a good build).
	if ((doShots)) && [[ -x "${SHOTS_HOOK}" ]]; then
		fSection "$(date "+%Y%m%d-%H%M%S") Screenshots"
		if "${SHOTS_HOOK}"; then fEcho "Screenshots refreshed."
		else fEcho "WARNING: screenshot refresh failed (non-fatal); continuing."; fi
		fEcho_ResetBlankCounter
	fi

	## Stage: backup + publish.
	if ((doPublish)); then
		fSection "$(date "+%Y%m%d-%H%M%S") Backup + publish"
		if [[ -n "${publishMsg}" ]]; then
			## Hands-off: quiet env skips n8git's prompt; the editor helper fills the
			## empty commit message so `git commit` won't open an interactive editor.
			GIT_BACKUP_AND_PUBLISH_QUIET=1  GIT_AUTO_MESSAGE="${publishMsg}" \
				GIT_EDITOR="${meDir}/utility/git-auto-msg.bash"  "${gitPublish}"
		else
			"${gitPublish}"
		fi
	fi

	## Done
	if ((! doQuietly)); then fSection "${meName}: Done."; fEcho_Clean; fi
}


#•••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
fCleanup(){ ((! doQuietly)) && fEcho_Clean; :;}


#•••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
## Generic functions (owner's shared library)
fMustBeInPath(){
	local -r programToCheckForInPath="${1:-}"
	if [[ -z "${programToCheckForInPath}" ]]; then
		fThrowError "No program specified."  "${FUNCNAME[0]}"; return 1
	elif [[ -z "$(which ${programToCheckForInPath} 2>/dev/null || true)" ]]; then
		fThrowError "Not found in path: ${programToCheckForInPath}"; return 1
	fi ;:;}
fIntroPromptToContinue(){
	{ ((doQuietly)) || ((! doPromptToContinue)); } && return 0
	fPromptYN "Continue? (y|n): "  ||  { fEcho "User aborted."; return 1; }; }
fPromptYN(){
	((doQuietly)) && return 0
	local promptStr="${1:-}"
	[[ -z "${promptStr}" ]] && promptStr="Continue? (y|n): "
	read -r -p "${promptStr}" userAnswer
	fEcho_ResetBlankCounter
	{ [[ "${userAnswer,,}" == "y" ]] && return 0; } || return 1; }

## Echo-related (minified but not obfuscated)
declare -gi _wasLastEchoBlank=0
declare -gi _isEchoInRawInlineMode=0
fEcho_ResetBlankCounter()     { _wasLastEchoBlank=0;      }
fEcho_WasLastEchoBlank_Set()  { { [[ "${1:-}" == "1" ]] && _wasLastEchoBlank=1; } || _wasLastEchoBlank=0;  }
fEcho_IsInRawInlineMode_Set() { { [[ "${1:-}" == "1" ]] && _isEchoInRawInlineMode=1; } || { _isEchoInRawInlineMode=0; _wasLastEchoBlank=0; echo; }; }
fEcho_Clean_byref(){
	[[ -v 1 ]] || fThrowError "Calling function must pass a nameref (string to echo) as arg1."
	local -n ptr_ToEcho_t5jf2=$1
	((_isEchoInRawInlineMode)) && fEcho_IsInRawInlineMode_Set 0
	if [[ -n "${ptr_ToEcho_t5jf2}" ]]; then
		echo -e "${ptr_ToEcho_t5jf2}"
		_wasLastEchoBlank=0
	elif [[ $_wasLastEchoBlank -eq 0 ]]; then
		echo
		_wasLastEchoBlank=1
	fi
}
fEcho_Clean()        { local -r toEcho="${1:-}"; fEcho_Clean_byref toEcho; }
fEcho()              { { [[ -z "${1:-}" ]] && fEcho_Clean ""; } || { local -r toEcho="[ ${1:-} ]"; fEcho_Clean_byref toEcho; }; }
fEcho_Force()        { _wasLastEchoBlank=0; fEcho "${1:-}"; }
fEcho_Clean_Force()  { _wasLastEchoBlank=0; local -r toEcho="${1:-}"; fEcho_Clean_byref toEcho; }

## Error-handling
declare -i _wasCleanupRun=0
declare -i _doExitOnThrow=0
declare -i _ErrVal=0
_fSingleExitPoint(){
	local -r signal="${1:-}"; local -r lineNum="${2:-}"; local -r exitCode="${3:-}"
	local -r errCommand="$BASH_COMMAND"
	_ErrVal=$exitCode
	if [[ "${signal}" == "INT" ]]; then
		fEcho_Force; echo "User interrupted." >&2; fEcho_ResetBlankCounter; fCleanup; exit 1
	elif [[ "${exitCode}" != "0" ]] && [[ "${exitCode}" != "1" ]]; then
		fEcho_Clean
		echo -e "Signal .....: '${signal}'"      >&2
		echo -e "Err# .......: '${exitCode}'"     >&2
		echo -e "At line# ...: '${lineNum}'"      >&2
		echo -e "Command# ...: '${errCommand}'"   >&2
		fEcho_Clean_Force; fCleanup
	else
		fCleanup
	fi ;}
_fTrap_Exit(){  if [[ "${_wasCleanupRun}" == "0" ]]; then _wasCleanupRun=1; _fSingleExitPoint "${@}"; fi ;}
_fTrap_Error(){ if [[ "${_wasCleanupRun}" == "0" ]]; then _wasCleanupRun=1; fEcho_ResetBlankCounter; _fSingleExitPoint "${@}"; fi ;}
fThrowError(){
	local errMsg="${1:-}"; [[ -z "${errMsg}" ]] && errMsg="An error occurred."
	local meNameLocal="${meName:-}"; [[ -z "${meNameLocal}" ]] && meNameLocal="$(basename "${BASH_SOURCE[0]}")"
	[[ -n "${meNameLocal}" ]] && errMsg="${meNameLocal}: ${errMsg}"
	fEcho_Clean; echo -e "${errMsg}" >&2; fEcho_ResetBlankCounter
	_ErrVal=1
	{ ((_doExitOnThrow)) && exit 1; } || return 1; }
fDefineTrap_Error_Fatal(){ :; _ErrVal=0; _doExitOnThrow=0; trap '_fTrap_Error ERR ${LINENO} $? $_' ERR; set -e; }
fDefineTrap_Error_Fatal
trap '_fTrap_Error SIGHUP  ${LINENO} $? $_' SIGHUP
trap '_fTrap_Error SIGINT  ${LINENO} $? $_' SIGINT
trap '_fTrap_Error SIGTERM ${LINENO} $? $_' SIGTERM
trap '_fTrap_Exit  EXIT    ${LINENO} $? $_' EXIT
trap '_fTrap_Exit  INT     ${LINENO} $? $_' INT
trap '_fTrap_Exit  TERM    ${LINENO} $? $_' TERM


#•••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
# Script entry point

## Bash environment settings
 set -u
 set -e
 set -E
 set -o pipefail
 shopt -s inherit_errexit
 shopt -s dotglob
 shopt -s globstar

## Common constants
if [[ -z "${serialDT+x}" ]]; then
	declare -r mePath="$(realpath -e "${BASH_SOURCE[0]}")"
	declare -r meName="$(basename "${mePath}")"
	declare -r meDir="$(dirname "${mePath}")"
	declare -r serialDT="$(date "+%Y%m%d-%H%M%S")"
fi

## Load per-project settings. Commands run from the source dir (github/), which is meDir/..
source "${meDir}/config.bash"
cd "${meDir}/.."

## Invoke main
fMain  "${@}"


##	Script history:
##		- 2026-07-04 JC: Rebuilt from the convert-base template for this Python project.
##			Split settings into config.bash, added -q/--quiet, -m/--message, --quick,
##			letterbox output, hands-off publish, and a screenshot stage.
