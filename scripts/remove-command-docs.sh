#!/bin/sh

# Remove command documenation in the target document

sed '/<!-- start command docs/,/<!-- end command docs/ {
	//!d
	}' "$1"
