#!/bin/sh

# Generate markdown documentation from the help output of commands
# listed in the target document.

awk '/<!-- start command list -->/,/<!-- end command list -->/ {print}' "$1" |
	sed -n '/^- / s/- \[\(.*\)](.*)$/\1/p' |
	xargs -iCMD sh -c '
		echo "Processing CMD" >&2;
		echo "### CMD";
		echo;
		echo "\`\`\`";
		[ "CMD" == "common options" ] && cmd="" || cmd="CMD"
		tmv71 $cmd --help;
		echo "\`\`\`";
		echo
		'
