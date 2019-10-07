#!/bin/sh

# Generate markdown documentation from the help output of commands
# listed in the target document.

awk '/<!-- start command list -->/,/<!-- end command list -->/ {print}' "$1" |
	sed -n '/^- / s/- \[\(.*\)](.*)$/\1/p' |
	xargs -iCMD sh -c '
		echo "### CMD";
		echo;
		echo "\`\`\`";
		tmv71 -K -p /dev/ttyKEYSPAN0 -s 9600 CMD --help;
		echo "\`\`\`";
		echo
		'
