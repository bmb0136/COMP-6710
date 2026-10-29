#!/usr/bin/env bash

set -euo pipefail

python3 w7.py
cat unique_crashes.json | jq -r '.[:10] | map(. | "Inputs: \(.v1), \(.v2)\nError: \(.error)") | join("\n\n")' > crashes.txt

tar -cf w7.tar w7.py crashes.txt
gzip -f w7.tar

rm crashes.txt
