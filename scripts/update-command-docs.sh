#!/bin/sh

# Update README.md with the help output of commands listed in the "Available
# commands" section.

tmpfile=$(mktemp docs.XXXXXX)
trap "rm -f $tmpfile" EXIT
sh scripts/remove-command-docs.sh README.md > $tmpfile

sed -n '1,/^<!-- start command docs/ p' $tmpfile > README.md
sh scripts/gen-command-docs.sh $tmpfile >> README.md
sed -n '/^<!-- end command docs/,$ p' $tmpfile >> README.md
