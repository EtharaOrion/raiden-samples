#!/bin/bash


set -uxo pipefail
SCRIPT_DIR="$(cd "$(dirname "$0")" && pwd)"
TASK_TOML="$SCRIPT_DIR/../task.toml"
cd /workspace
mkdir -p /logs/verifier

export PYTHONPATH="/opt/test-libs${PYTHONPATH:+:}${PYTHONPATH:-}"

python -m pytest "$SCRIPT_DIR" -v --tb=short -p no:randomly \
    --junit-xml=/logs/verifier/results.xml \
    > /logs/verifier/pytest_output.log 2>&1
cat /logs/verifier/pytest_output.log

TASK_TOML="$TASK_TOML" python3 << 'PY' > /logs/verifier/reward.txt
import os, re, sys, xml.etree.ElementTree as ET
from pathlib import Path

XML = "/logs/verifier/results.xml"
TOML = os.environ.get("TASK_TOML", "")


expected = None
if TOML and Path(TOML).exists():
    for line in Path(TOML).read_text().splitlines():
        m = re.match(r"\s*tests_shipped\s*=\s*(\d+)", line)
        if m:
            expected = int(m.group(1))
            break

try:
    root = ET.parse(XML).getroot()
except Exception as e:
    sys.stderr.write(f"reward parser v2: could not parse {XML}: {e}\n")
    print("0.0")
    sys.exit(0)


suites = root.findall("testsuite") if root.tag == "testsuites" else [root]
tests = failures = errors = skipped = 0
for s in suites:
    tests    += int(s.get("tests",    0) or 0)
    failures += int(s.get("failures", 0) or 0)
    errors   += int(s.get("errors",   0) or 0)
    skipped  += int(s.get("skipped",  0) or 0)
passed = tests - failures - errors - skipped


if expected is not None and tests < expected:
    sys.stderr.write(
        f"reward parser v2: COLLECTION DRIFT — task.toml.tests_shipped={expected} "
        f"but JUnit reports tests={tests}. Reward=0.\n"
    )
    print("0.0")
    sys.exit(0)


total = passed + failures + errors
print(round(passed / total, 4) if total else 0.0)
PY

REWARD=$(cat /logs/verifier/reward.txt)
echo "reward=$REWARD parser=v2"
exit 0
