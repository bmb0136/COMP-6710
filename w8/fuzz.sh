#!/usr/bin/env bash

set -euo pipefail

program=w8
afl-clang-fast -g -w $program.c -o $program
afl-fuzz -i /fuzzing-inputs/ -t 10000 -V $((5 * 60)) -o /output/ ./$program
