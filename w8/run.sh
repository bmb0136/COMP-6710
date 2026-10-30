#!/usr/bin/env bash

set -euo pipefail

echo removing old output
(rm -rf output || :) && mkdir output

echo building
docker build . -t w8

echo fuzzing
docker run -v "$(realpath ./output):/output" -it w8:latest bash ./fuzz.sh

notify-send --icon=utilities-terminal "Done fuzzing!" || :

echo chowning outputs
sudo chown -R "$(id -un)" ./output

