#/usr/bin/env bash

PROGRAM="./dist/FileOpener"
OUTPUTS="./outputs/"
INPUTS="./inputs/"
REPEATS=5

set -eu pipefail

run_test() {
	name="$1"
	echo "Running test $name..."
	shift
	f="$@"
	$PROGRAM $f &> "$OUTPUTS/$name.txt" || :
	log="$INPUTS/$name.txt"
	echo "Command: $PROGRAM $f" > $log
	echo "File:" >> $log
	if [ -f "$f" ]; then
		cat $f >> $log || :
	fi
}

main() {
	mkdir -p "$OUTPUTS" "$INPUTS"

	# case 1: no file
	for i in $(seq 1 $REPEATS); do
		run_test no_file_$i
	done

	# case 2: nonexistent
	for i in $(seq 1 $REPEATS); do
		run_test nonexistent_file_$i $(head -c 42 /dev/random | base64 | sed 's/[^a-zA-Z0-9]/_/g')
	done

	# case 3: directory
	for i in $(seq 1 $REPEATS); do
		run_test directory_$i $(mktemp -d)
	done

	# case 4: name too long
	for i in $(seq 1 $REPEATS); do
		run_test name_too_long_$i $(python3 -c 'print("".join(__import__("random").choices("abcdefghijklmnopqrstuvwxyz", k=100000)))')
	done

	# case 5: invalid encoding
	for i in $(seq 1 $REPEATS); do
		f=$(mktemp)
		head -c 42069 /dev/urandom > $f
		run_test invalid_encoding_$i $f
	done
}

main
