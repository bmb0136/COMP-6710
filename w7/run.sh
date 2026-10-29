#!/usr/bin/env bash

set -euo pipefail

python3 w7.py
cat unique_crashes.json | jq -r '.[:10] | map(. | "Inputs: \(.v1), \(.v2)\nError:\(.error)") | join("\n\n")' > 10crashes.txt
cat 10crashes.txt

tar -cvf w7.tar w7.py 10crashes.txt
gzip w7.tar

rm 10crashes.txt
