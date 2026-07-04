#!/bin/bash
#  shellcheck disable=2016  ## explicit '$' in single quotes is intentional.
#  shellcheck disable=2086  ## integer word-splitting is fine.

##	Purpose:
##		- Refresh the README screenshot gallery. Captures the app on a headless
##		  display in a few representative states, downsamples the originals, and
##		  regenerates the gallery block in README.md.
##		- Full-size PNGs go in assets/screenshots/large, thumbnails (max 640 on the
##		  long side, shrink-only) in assets/screenshots/small. Clicking a thumbnail
##		  opens the original.
##	History: At bottom of script.

##	Copyright © 2026 Jim Collier (ID: 1cv◂‡Vᛦ)
##	Licensed under The MIT License (MIT). Full text at:
##		https://mit-license.org/
##	SPDX-License-Identifier: MIT


set -Eeuo pipefail

meDir="$(cd "$(dirname "${BASH_SOURCE[0]}")" && pwd)"
srcDir="$(cd "${meDir}/../.." && pwd)"          ## the github/ source dir
largeDir="${srcDir}/assets/screenshots/large"
smallDir="${srcDir}/assets/screenshots/small"
readme="${srcDir}/README.md"
maxLong=640                                     ## thumbnail longest side


## Owner's fEcho output helpers + letterbox section rule.
declare -gi _wasLastEchoBlank=0
_sectionBar="•••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••••"
fEcho_Clean(){
	local -r s="${1:-}"
	if [[ -n "${s}" ]]; then echo -e "${s}"; _wasLastEchoBlank=0
	elif ((! _wasLastEchoBlank)); then echo; _wasLastEchoBlank=1; fi
}
fEcho(){ { [[ -z "${1:-}" ]] && fEcho_Clean ""; } || fEcho_Clean "[ ${1} ]"; }
fSection(){ fEcho_Clean ""; fEcho_Clean "${_sectionBar}"; fEcho "${1:-}"; }


## Human-readable caption per shot name (keep in sync with screenshots.py).
fCaption(){ case "$1" in
	01-calc)      echo "Scientific calculator" ;;
	02-graph)     echo "Function graphing" ;;
	03-python)    echo "Python editor and console" ;;
	04-calc-2nd)  echo "2nd-function keypad" ;;
	*)            echo "${1}" ;;
esac; }


fMain(){
	## Dependencies.
	for dep in xvfb-run import python3; do
		command -v "${dep}" >/dev/null 2>&1 || { echo "screenshots: missing '${dep}'" >&2; return 1; }
	done

	mkdir -p "${largeDir}" "${smallDir}"

	## Capture the originals on a private headless display.
	fSection "Capturing"
	xvfb-run -a -s "-screen 0 1920x1080x24" python3 "${meDir}/screenshots.py" "${largeDir}"

	## Strip volatile metadata from the captures so re-runs are byte-identical
	## (no timestamp churn showing up as a git diff), then downsample to
	## thumbnails (shrink-only; '>' never upsamples). Thumbnails are stripped too.
	fSection "Downsampling"
	local png baseName
	for png in "${largeDir}"/*.png; do
		[[ -e "${png}" ]] || continue
		baseName="$(basename "${png}")"
		fStripMeta "${png}"
		fResizeStripped "${png}" "${smallDir}/${baseName}"
		fEcho_Clean "  ${baseName}"
	done

	## Rebuild the README gallery block.
	fSection "Updating README"
	fBuildGallery > "${srcDir}/.shots.block"
	fInjectGallery
	rm -f "${srcDir}/.shots.block"
	fEcho_Clean "  ${readme}"
}


## ImageMagick wrapper: prefer `magick` (v7), fall back to `convert` (v6).
## '-strip' plus excluding the date/time chunks drops the only bytes that vary
## between otherwise-identical runs, so committed images stay stable.
fMagick(){ if command -v magick >/dev/null 2>&1; then magick "$@"; else convert "$@"; fi; }
fStripMeta(){ fMagick "$1" -strip -define png:exclude-chunks=date,time "$1"; }
fResizeStripped(){ fMagick "$1" -resize "${maxLong}x${maxLong}>" -strip -define png:exclude-chunks=date,time "$2"; }


## Emit the responsive gallery HTML. Percentage widths let the thumbnails shrink
## together and wrap on narrow screens; each links to its full-size original.
fBuildGallery(){
	echo '<!-- SCREENSHOTS:START -->'
	echo '<div align="center">'
	local png baseName shotName caption
	for png in "${smallDir}"/*.png; do
		[[ -e "${png}" ]] || continue
		baseName="$(basename "${png}")"; shotName="${baseName%.png}"; caption="$(fCaption "${shotName}")"
		echo "<a href=\"assets/screenshots/large/${baseName}\"><img src=\"assets/screenshots/small/${baseName}\" alt=\"${caption}\" title=\"${caption}\" width=\"23%\"></a>"
	done
	echo '</div>'
	echo '<!-- SCREENSHOTS:END -->'
}


## Replace the block between the markers. If they're absent, add a Screenshots
## section just before the copyright section (or at end of file).
fInjectGallery(){
	if grep -q '<!-- SCREENSHOTS:START -->' "${readme}"; then
		awk '
			/<!-- SCREENSHOTS:START -->/ { print_block(); skip=1 }
			/<!-- SCREENSHOTS:END -->/   { skip=0; next }
			!skip { print }
			function print_block(){ while ((getline line < BLOCK) > 0) print line; close(BLOCK) }
		' BLOCK="${srcDir}/.shots.block" "${readme}" > "${readme}.tmp"
	else
		awk '
			/^## Copyright and license/ && !done { print "## Screenshots"; print ""; print_block(); print ""; done=1 }
			{ print }
			END { if (!done){ print ""; print "## Screenshots"; print ""; print_block() } }
			function print_block(){ while ((getline line < BLOCK) > 0) print line; close(BLOCK) }
		' BLOCK="${srcDir}/.shots.block" "${readme}" > "${readme}.tmp"
	fi
	mv "${readme}.tmp" "${readme}"
}


fMain "${@}"


##	History:
##		- 2026-07-04 JC: Created.
