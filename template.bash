#!/bin/env bash

#  shellcheck disable=2001  ## 'See if you can use ${variable//search/replace} instead.' Complains about good uses of sed.
#  shellcheck disable=2002  ## 'Useless use of cat.'
#  shellcheck disable=2016  ## 'Expressions don't expand in single quotes, use double quotes for that.' I know, and I often want an explicit '$'.
#  shellcheck disable=2034  ## 'variable appears unused.' Complains about valid use of variable indirection (e.g. later use of local -n var=$1)
#  shellcheck disable=2046  ## 'Quote to prevent word-splitting.' (OK for integers.)
#  shellcheck disable=2086  ## 'Double quote to prevent globbing and word splitting.' (OK for integers.)
#  shellcheck disable=2119  ## 'Use foo "$@" if function's $1 should mean script's $1.' Confusing and inapplicable.
#  shellcheck disable=2120  ## 'Foo references arguments, but none are ever passed.' Valid function argument overloading.
#  shellcheck disable=2128  ## 'Expanding an array without an index only gives the element in the index 0.' False hits on associative arrays.
#  shellcheck disable=2143  ## 'Use grep -q instead of echo | grep'
#  shellcheck disable=2155  ## 'Declare and assign separately to avoid masking return values.' Cumbersome and unnecessary. For integers it's sometimes required to even come into existence for counters.
#  shellcheck disable=2162  ## 'read without -r will mangle backslashes.'
#  shellcheck disable=2178  ## 'Variable was used as an array but is now assigned a string.' False hits on associative arrays with e.g. 'local -n assocArray=$1'.
#  shellcheck disable=2181  ## 'Check exit code directly, not indirectly with $?.'
#  shellcheck disable=2317  ## 'Can't reach.' (I.e. an 'exit' is used for debugging - and makes an unusable visual mess.)
## shellcheck disable=2004  ## '$/${} is unnecessary on arithmetic variables.' Inappropriate complaining?
## shellcheck disable=2053  ## 'Quote the right-hand side of = in [[ ]] to prevent glob matching.' Disable for Yoda Notation.

##	Purpose: See fShowAbout_Local() below.
##	Template copyright: At bottom of script.
##	History: At bottom of script. (Maintained separately from and/or in addition to, cloud-based version control.)


##•••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
## Module settings and constants

if [[ ! -v doQuietly ]]; then
	## Required by this template
	declare -gri ARGS_AT_LEAST_ONE_IS_REQUIRED=0
	declare -gri ARGS_MAX_POSITIONAL_COUNT=0
fi
if [[ ! -v THIS_FILEPATH ]]; then
	## Required by n8mod_core_v1
	declare -gr  THIS_FILEPATH="$(realpath -e "${0}")"
	declare -gr  THIS_FILENAME="$(basename "${THIS_FILEPATH}")"
	declare -gr  THIS_DIRPATH="$(dirname "${THIS_FILEPATH}")"
	declare -gri DO_CHAIN_SUDO=1  ## Don't have to use
	## Populated by n8mod_core_v1
	declare -g   SERIAL_DATETIME
	declare -g   RELAUNCH_SENTINELVAL
fi
if [[ ! -v THIS_VERSION ]]; then
	## Required by n8mod_user_v1
	declare -gi doQuietly=0
	declare -gi doPromptToContinue=1
	declare -gr THIS_VERSION="1.0.0-beta1"
	declare -gr THIS_BUILD="1n0pagv"
	declare -gr THIS_COPYRIGHT_YEARS="2011-2026"
	declare -gr THIS_AUTHOR="Jim Collier"
	declare -gr LICENSE_SPDX="GPL-2.0-or-later"   ## Valid so far: GPL-2.0-or-later
fi


##•••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
fShowAbout_Local(){
	local aboutStr=""
	#         X-------------------------------------------------------------------------------X
	aboutStr+="A thing that does some stuff, like:\n"
	aboutStr+="  • This.\n"
	aboutStr+="  • And that."
	#         X-------------------------------------------------------------------------------X
	fShowAbout aboutStr
}

##•••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
fShowSyntax_Local(){
	local syntaxStr=""
	#          X-------------------------------------------------------------------------------X
	syntaxStr+="Arguments:\n"
	syntaxStr+="  --quiet\n"
	syntaxStr+="      [optional]: Be less verbose, and don't prompt user to continue.\n"
	syntaxStr+="  --help, --about, --version [or -h, -a, -v]"
	#          X-------------------------------------------------------------------------------X
	fShowSyntax syntaxStr
}


##•••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
## Invoked by n8mod_core, after this script invokes fInit().
fMain(){ :;

	## Settings
	local ogUSER="" ; fGetOgUserName ogUSER             ; readonly ogUSER  ## Not required by anything in template.
	local ogHOME="" ; fGetOgUserHome ogHOME "${ogUSER}" ; readonly ogHOME  ## Not required by anything in template.

	## Pre-arg validation

	## Arguments
	local -a allArgsArr=()
	fParseArgs  "${@}"
	readonly allArgsArr

	## Post-arg validation

	## Prompt to continue
	if ((! doQuietly)); then
		fShowCopyright
		fShowAbout_Local
		fEcho_Clean "Some info ...............: ${USER}"
		fEcho_Clean "More info ...............: ${HOME}"
		fIntroPromptToContinue  ""
		fEcho_Clean
	fi

	## Done; either fChainToFunc() -> fMain_Chained() returned, or this script run in a sudo subshell [running only fMain_Chained()] returned.
	((! doQuietly)) && { fEcho; fEcho "Done."; fEcho; }
}


#••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
fMain_Chained(){
	## Only needed this function, if $DO_CHAIN_SUDO==1, and you intend to invoke `fChainToFunc 'fMain_Chained'` in fMain().
	## Example invocation:
	##	fChainToFunc  'fMain_Chained'  "$(declare -p  doQuietly  ogUSER  ogHOME)"
	[[ -n "${1:-}" ]] && eval "${1:-}"  ## Restore caller's serialized variables [or fArgs_*]. New scope is local to this function.
	((! doQuietly)) && fEcho_Clean

	## Revalidate
	[[   -z "${doQuietly}" ]]                && { fThrowError "Arg not set: doQuietly" ; return 1; }
	[[   -z "${ogUSER}" ]]                   && { fThrowError "Arg not set: ogUSER" ; return 1; }
	[[   -z "${ogHOME}" ]]                   && { fThrowError "Arg not set: ogHOME" ; return 1; }

}

#•••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
## This needs to be made generic. Until then, we have this per-script.
fParseArgs(){
	## Look for stars "✶✶✶✶✶✶✶✶" for places to custom-modify unique instances of this function.

	## Check for need to show help etc.
	case " ${*,,} " in
		*" -h "*|*" --help "*|*" -help "*)                               fShowCopyright; fShowAbout_Local; fShowSyntax_Local  ; exit 0 ;;
		*" -a "*|*" --about "*|*" -about "*)                             fShowCopyright; fShowAbout_Local                 ; exit 0 ;;
		*" -v "*|*" --version "*|*" -version "*|*" --ver "|*" -ver "**)  fShowVersion; doQuietly=1                        ; exit 0 ;;
	esac

	## Check for need to show help
	((ARGS_AT_LEAST_ONE_IS_REQUIRED  &&  $# <= 0)) && { fShowCopyright; fShowAbout_Local; fShowSyntax_Local; return 1; }

	## GENERIC: Variables for loop
	local -ri MAX_EMPTY_SEQUENTIAL_ARGS=10  ## Bail after this many consecutive empty args
	local    tmpStr=""
	local    currentArg=""
	local    lastSwitch=""
	local -i switchCounter=0
	local -i expectingSwitchParamForNextArg=0
	local -i positionalArgCounter=0
	local -i emptyRunCount=0

	## Process arguments
	for currentArg in "${@}"; do
		#fEcho_Clean "Debug: currentArg ........: '${currentArg}'"

		## Track consecutive empty args, bail if too many.
		if [[ -z "${currentArg}" ]]; then
			(( ++emptyRunCount ))
			(( emptyRunCount >= MAX_EMPTY_SEQUENTIAL_ARGS )) && break
			continue  ## If empty but not bailing, skip to next
		else
			emptyRunCount=0
		fi

		## Sanitize quotes
		currentArg="${currentArg//\"/″}"; currentArg="${currentArg//\'/′}"

		## Test if an option switch or not
		if [[ -n "$(echo "${currentArg}" | grep -P "^\-(\-?)[^\ \-]" 2>/dev/null || true)" ]]; then
			## It's an option (either unary or long-option, we don't know yet)
			#fEcho_Clean "Debug: option ............: '${currentArg}'"

			## Check if this was supposed to NOT be a unary switch (eg expecting a parameter after previous long-option)
			((expectingSwitchParamForNextArg)) && fThrowError "Expecting a long-option argument for '${lastSwitch}', instead got another option '${currentArg}'."
			((++switchCounter))

			## Validate switches, and act on unary switches
			lastSwitchAsPassed="${currentArg}"
			tmpStr="${currentArg,,}"

			## Strip switch dashes off
			while [[ "${tmpStr}" == -* ]]; do tmpStr="${tmpStr#-}"; done
			lastSwitch="${tmpStr}" ## Remember lastSwitch

			case "${tmpStr}" in

				## ✶✶✶✶✶✶✶✶ PUT CUSTOM UNARY SWITCH TESTS AND PARENT BOOLEAN VARIABLE ASSIGNMENTS HERE
				"quiet")  doQuiet=1  ;;

				## ✶✶✶✶✶✶✶✶ PUT TESTS FOR CUSTOM LONG-OPTION LOGIC THAT EXPECTS AN ARGUMENT TO FOLLOW, HERE
			#	"long-option-with-arg-to-follow") expectingSwitchParamForNextArg=1 ;;

				## ¯\_(ツ)_/¯
				*) fThrowError  "Unexpected option in this context: '${currentArg}'."  ;;

			esac
		else
			## It's not an option switch; could be a long-option argument, or a positional arg

			if ((expectingSwitchParamForNextArg)); then :
				## Now we know to expecting an long-option argument
				#fEcho_Clean "Debug: arg for long-option: '${lastSwitch}': '${currentArg}'"

				## ✶✶✶✶✶✶✶✶ PUT CUSTOM LONG-OPTION ARGUMENT TESTS AND PARENT VARIABLE ASSIGNMENTS HERE
			#	case "${lastSwitch,,}" in
			#		"long-option-with-arg-to-follow") someParentVariable="${currentArg}" ;;
			#		*)                                fThrowError "Unkown option: '${lastSwitchAsPassed}', current parameter: '${currentArg}'." ;;  ## A redundant check.
			#	esac
			#	expectingSwitchParamForNextArg=0

			else
				## Well it must be a positional arg then.
				((++positionalArgCounter))
				((positionalArgCounter > ARGS_MAX_POSITIONAL_COUNT))  && fThrowError "Too many positional arguments: ${positionalArgCounter}, for max of ${ARGS_MAX_POSITIONAL_COUNT}."
				#fEcho_Clean "Debug: positional arg #${positionalArgCounter}: '${currentArg}'"

				## ✶✶✶✶✶✶✶✶ PUT CUSTOM POSITIONAL ARG LOGIC HERE (only use one of the following methods, delete the other)

				## Assign parent variables; Method 1: argument counter (less flexible but best for simple input)
			#	case $positionalArgCounter in
			#		1) stringArg="${currentArg}"      ;;
			#		2) arg_intArg="${currentArg}"     ;;
			#		*) fThrowError "Unexpected positional argument # ${positionalArgCounter}: '${currentArg}'." ;;
			#	esac

			fi
		fi
	done; :
	((expectingSwitchParamForNextArg)) && fThrowError "Never received a parameter for switch '--${lastSwitch}'."

:;}


#••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
fCleanup(){
	if ((! doQuietly)); then
		fEcho_Clean
	fi
}
















##•••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
## Generic boilerplate in every script

fLoadModule_v1(){
	## Purpose: Loads a module by name.
	## E.g.: fLoadModule_v1  'n8mod_core_v1'
	local -r arg_ModuleName="${1:-}"  # ; shift || :  ## Module name
	local resolvedPath
	fResolvePath_v1  resolvedPath  "${arg_ModuleName}"
	# shellcheck source=/dev/null
	[[ -f "${resolvedPath}" ]] && source "${resolvedPath}"
		## Note that since we're source'ing inside a function, and regular 'declare' in global
		## scope within those modules, will actually be local scope to this function. The fix
		## is to just idiomatically always declare global variables/constants with `-g`.
:;}

fResolvePath_v1(){
	## Purpose: Resolves an argument to a canonical full path, while being careful to not be too broad as to resolve to something else with the same name.
	## Searches common 'include|lib'-like sub-paths, then if arg is a single filename, the system $PATH.
	## Subshells and external tools are OK in this very early function that preceeds any modules being loaded.
	## Validate nameref args
	[[ -v 1 ]] || { echo -e "\nError in $(basename "${BASH_SOURCE[0]}")·${FUNCNAME[0]}(): Calling function must pass a nameref to receive this function's output, as arg1.\n"                           ; return 1; }
	## Gather args
	local -n ref_Return_ResolvedPath_t4rej=$1  ; shift || :  ## Parent variable to store fully resolved path in.
	local -r nameOrPath="${1:-}"               ; shift || :  ## File or folder path (relative or absolute). If an executable file, can be just a name to search in $PATH, to fully resolve.
	local -i mustExist=${1:-1}                 ; shift || :  ## 1 [default]: path must exist or error occurs. 0: Just rationalize paths, doesn't have to exist.
	## Validate
	[[ "${nameOrPath}" ]] || { echo -e "\nError in $(basename "${BASH_SOURCE[0]}")·${FUNCNAME[0]}(): Path or executable name not specified.\n" ; return 1; }
	## Init
	ref_Return_ResolvedPath_t4rej=""
	## Obvious test, as-is
	[[ -e "${nameOrPath}" ]] && { ref_Return_ResolvedPath_t4rej="$(realpath -e "${nameOrPath}")"; return 0; }
	## Test file with common sub-paths
	local -r mePath_t4rej="$(dirname "${BASH_SOURCE[0]}")"  ## Pathspec to this script.
	local -a tryRelSubs=('/'  '/lib/'  '/include/'  '/includes/') ; local -a tryRelPaths=()  ## Common generic library subdirs.
	for nextSub in "${tryRelSubs[@]}"; do tryRelPaths+=("${BASH_SOURCE[0]}.d${nextSub}${nameOrPath}") ; done  ## "[this script's full pathspec].d/[each common subdir]/[argument]".
	for nextSub in "${tryRelSubs[@]}"; do tryRelPaths+=("${mePath_t4rej}${nextSub}${nameOrPath}")     ; done  ## "[this script's folder]/[each common subdir]/[argument]".
	for nextPath in "${tryRelPaths[@]}"; do [[ -e "${nextPath}" ]] && { ref_Return_ResolvedPath_t4rej="$(realpath -e "${nextPath}")"; return 0; }; done  ## Return realpath if found in the first match.
	local testPath=""
	## Try 'which', if arg is a single file.
	if [[ "${nameOrPath}" != */* ]]; then
		testPath="$(which "${nameOrPath}" 2>/dev/null || true)"
		[[ -n "${testPath}" ]] && { ref_Return_ResolvedPath_t4rej="$(realpath -e "${testPath}")"; return 0; }  ## Return 'which'
	fi
	## Haven't matched yet: revert to original argument
	testPath="${nameOrPath}"
	if ((mustExist)); then
		testPath="$(realpath -e "${testPath}" 2>/dev/null || true)"
		[[ -n "${testPath}" && -e "${testPath}" ]] || { echo -e "\nError in $(basename "${BASH_SOURCE[0]}")·${FUNCNAME[0]}(): Could not resolve path '${nameOrPath}' [£ǝŔs].\n"; return 1; }
	else
		testPath="$(realpath -m "${testPath}" 2>/dev/null || true)"
		[[ -n "${testPath}" ]] || { echo -e "\nError in $(basename "${BASH_SOURCE[0]}")·${FUNCNAME[0]}(): Could not resolve even optionally nonexistent path '${nameOrPath}' [£ǝŔs].\n"; return 1; }
	fi
	## Success
	ref_Return_ResolvedPath_t4rej="${testPath}"
}

## Bash environment settings
 set -u  #..................: Require variable declaration. Stronger than mere linting.
 set -e  #..................: Exit on errors.
 set -E  #..................: Propagate ERR trap settings into functions, command substitutions, and subshells.
 set   -o pipefail  #.......: Make sure all stages of piped commands also fail the same.
 shopt -s inherit_errexit  #: Propagate 'set -e' ........ into functions, command substitutions, and subshells. Will fail on Bash <4.4.
 shopt -s dotglob  #........: Include usually-hidden 'dotfiles' in '*' glob operations - usually desired.
 shopt -s globstar  #.......: ** matches more stuff including recursion.

## Check if sourced
declare -i isSourced_t5ja1=0; [[ "${BASH_SOURCE[0]}" == "${0}" ]] || isSourced_t5ja1=1
#((isSourced_t5ja1)) || { echo -e "\nError in $(basename "${BASH_SOURCE[0]}"): This script is meant to be 'sourced' from within another script.\n"; exit 1; }
{ ((isSourced_t5ja1)) && [[ "${1:-}" != '--unit-test' ]]; }  &&  { echo -e "\nError in $(basename "${BASH_SOURCE[0]}"): This script is not meant to be 'sourced' from within another script, unless for unit-testing.\n"; exit 1; }

## Load modules
	[[ -v N8MOD_CORE_V1_IS_LOADED       ]] || fLoadModule_v1  'n8mod_core_v1'
	[[ -v N8MOD_INTERACT_V1_IS_LOADED   ]] || fLoadModule_v1  'n8mod_interact_v1'
	[[ -v N8MOD_STRING_V1_IS_LOADED     ]] || fLoadModule_v1  'n8mod_string_v1'
#	[[ -v N8MOD_NUMBER_V1_IS_LOADED     ]] || fLoadModule_v1  'n8mod_number_v1'
#	[[ -v N8MOD_FILESYS_V1_IS_LOADED    ]] || fLoadModule_v1  'n8mod_filesys_v1'
#	[[ -v N8MOD_PROCESS_V1_IS_LOADED    ]] || fLoadModule_v1  'n8mod_process_v1'
#	[[ -v N8MOD_LOGGING_V1_IS_LOADED    ]] || fLoadModule_v1  'n8mod_logging_v1'
#	[[ -v N8MOD_ARRAY_V1_IS_LOADED      ]] || fLoadModule_v1  'n8mod_array_v1'
#	[[ -v N8MOD_OOP_V1_IS_LOADED        ]] || fLoadModule_v1  'n8mod_oop_v1'
#	[[ -v N8MOD_ZFS_V1_IS_LOADED        ]] || fLoadModule_v1  'n8mod_zfs_v1'
#	[[ -v N8MOD_BTRFS_V1_IS_LOADED      ]] || fLoadModule_v1  'n8mod_btrfs_v1'
#	[[ -v N8MOD_SQL_V1_IS_LOADED        ]] || fLoadModule_v1  'n8mod_sql_v1'
#	[[ -v N8MOD_SQLITE3_V1_IS_LOADED    ]] || fLoadModule_v1  'n8mod_sqlite3_v1'
#	[[ -v N8MOD_POSTGRESQL_V1_IS_LOADED ]] || fLoadModule_v1  'n8mod_postgresql_v1'

## Kick everything off (unless unit-testing)
[[ "${1:-}" == '--unit-test' ]] || fInit "${@}"


##•••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
## Copyright and license:
##		template.bash from https://github.com/jim-collier/x9bash5-template
##		Copyright © 2026 Jim Collier (ID: 1cv◂‡Vᛦ)
##		Licenced under GPL v2.0-or-later. No warranty.
##
##		SPDX-License-Identifier: GPL-2.0-or-later:
##
##		This program is free software: you can redistribute it and/or modify
##		it under the terms of the GNU General Public License as published by
##		the Free Software Foundation, either version 2 of the License, or
##		(at your option) any later version.
##
##		This program is distributed in the hope that it will be useful,
##		but WITHOUT ANY WARRANTY; without even the implied warranty of
##		MERCHANTABILITY or FITNESS FOR A PARTICULAR PURPOSE.  See the
##		GNU General Public License for more details.
##
##		You should have received a copy of the GNU General Public License
##		along with this program.  If not, see <https://www.gnu.org/licenses/>.

##•••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••
## History:
##		- 20260517 JC: Created.
