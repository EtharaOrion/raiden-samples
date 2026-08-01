#!/bin/bash
set -euxo pipefail
cd /workspace
git config --global --add safe.directory /workspace

DIR="$(dirname "$0")"
GOLDEN="$DIR/golden.diff"
REFERENCE="$DIR/reference.diff"

if [ -s "$GOLDEN" ]; then
  PATCH="$GOLDEN"
elif [ -s "$REFERENCE" ]; then
  PATCH="$REFERENCE"
else
  echo "solve.sh: no non-empty patch found (golden.diff or reference.diff)" >&2
  exit 1
fi

git apply --verbose --reject "$PATCH"
chmod +x /workspace/submission/aws 2>/dev/null || true
