#!/bin/bash
set -euxo pipefail
mkdir -p /workspace/submission
cd /workspace
git config --global --add safe.directory /workspace
DIR="$(dirname "$0")"
GOLDEN="$DIR/golden.diff"
REFERENCE="$DIR/reference.diff"
CHOICE="${SOLVE_PATCH:-auto}"
case "$CHOICE" in
  golden)
    PATCH="$GOLDEN"
    ;;
  reference)
    PATCH="$REFERENCE"
    ;;
  auto|*)
    if [ -s "$GOLDEN" ]; then
      PATCH="$GOLDEN"
    elif [ -s "$REFERENCE" ]; then
      PATCH="$REFERENCE"
    else
      echo "solve.sh: no non-empty patch found (golden.diff or reference.diff)" >&2
      exit 1
    fi
    ;;
esac
if [ ! -s "$PATCH" ]; then
  echo "solve.sh: requested patch is empty: $PATCH" >&2
  exit 1
fi
git apply --verbose --reject "$PATCH"
if [ -f /workspace/submission/kubectl.go ] && [ ! -x /workspace/submission/kubectl ]; then
  ( cd /workspace/submission && go build -o kubectl . )
  chmod +x /workspace/submission/kubectl
fi
if [ -f /workspace/submission/kubectl-src/vendor/modules.txt ]; then
  ( cd /workspace/submission/kubectl-src && GOFLAGS=-mod=vendor go build -o /workspace/submission/kubectl ./cmd/kubectl ) || echo 'solve.sh: kubectl-src vendored go build failed; retaining pre-existing /workspace/submission/kubectl' >&2
  chmod +x /workspace/submission/kubectl 2>/dev/null || true
elif [ -f /workspace/submission/kubectl-src/go.mod ]; then
  ( cd /workspace/submission/kubectl-src && go build -o /workspace/submission/kubectl ./cmd/kubectl ) || echo 'solve.sh: kubectl-src go build failed; retaining pre-existing /workspace/submission/kubectl' >&2
  chmod +x /workspace/submission/kubectl 2>/dev/null || true
fi
