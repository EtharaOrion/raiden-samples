#!/bin/bash
set -euxo pipefail
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
if [ ! -f /workspace/submission/aws ] && [ -f /workspace/submission/main.py ]; then
  cat > /workspace/submission/aws <<'EOF'
#!/bin/bash
exec python /workspace/submission/main.py "$@"
EOF
fi
chmod +x /workspace/submission/aws 2>/dev/null || true
