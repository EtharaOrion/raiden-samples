"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

"""
Held-out behavioral tests for the verb-first kubectl-subset CLI.

Only the `cli` fixture (subprocess invoker for the submission entrypoint) and
standard pytest fixtures (tmp_path) are used. Any other fixture is accessed
defensively so this module stays importable/runnable even if the shipped
conftest does not expose it under the exact name we guess.
"""
import json
import time
import uuid

import pytest


def _rc(result):
    """Best-effort extraction of an integer return code from whatever the
    `cli` fixture returns (CompletedProcess-like object or tuple)."""
    if hasattr(result, "returncode"):
        return result.returncode
    if isinstance(result, tuple) and len(result) >= 1:
        return result[0]
    raise AssertionError(f"cannot extract returncode from {result!r}")


def _out(result):
    if hasattr(result, "stdout"):
        out = result.stdout
    elif isinstance(result, tuple) and len(result) >= 2:
        out = result[1]
    else:
        out = ""
    if isinstance(out, bytes):
        out = out.decode("utf-8", "replace")
    return out or ""


def _err(result):
    if hasattr(result, "stderr"):
        err = result.stderr
    elif isinstance(result, tuple) and len(result) >= 3:
        err = result[2]
    else:
        err = ""
    if isinstance(err, bytes):
        err = err.decode("utf-8", "replace")
    return err or ""


def _uniq(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _write(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


# ---------------------------------------------------------------------------
# Argument-parsing / dispatch behaviors
# ---------------------------------------------------------------------------

def test_resource_first_form_is_rejected(cli):
    """The CLI is strictly verb-first; `kubectl pods get` must not behave
    like `kubectl get pods` — it must fail (never succeed silently)."""
    result = cli("pods", "get")
    assert _rc(result) != 0


def test_unknown_flag_is_exit_2_with_invalid(cli):
    result = cli("get", "pods", "--totally-bogus-flag")
    assert _rc(result) == 2
    assert "invalid" in _err(result).lower()


def test_delete_missing_name_without_all_is_exit_2(cli):
    result = cli("delete", "pod")
    assert _rc(result) == 2
    combined = (_err(result) + _out(result)).lower()
    assert "invalid" in combined or "resource(s) were provided" in combined


def test_unknown_kind_is_runtime_failure_not_parse_error(cli):
    """An unrecognized but syntactically valid TYPE token must be a runtime
    (exit 1) error, not an argparse-style (exit 2) one."""
    result = cli("get", "totallynotakind123")
    assert _rc(result) == 1
    assert "invalid" not in _err(result).lower() or _rc(result) == 1


# ---------------------------------------------------------------------------
# create / apply / get / delete lifecycle & state consistency
# ---------------------------------------------------------------------------

def test_create_then_get_then_delete_lifecycle(cli, tmp_path):
    name = _uniq("cm")
    manifest = f"""
apiVersion: v1
kind: ConfigMap
metadata:
  name: {name}
data:
  foo: bar
"""
    path = _write(tmp_path, "cm.yaml", manifest)

    created = cli("create", "-f", path)
    assert _rc(created) == 0
    assert "created" in _out(created)

    got = cli("get", "configmap", name)
    assert _rc(got) == 0
    assert name in _out(got)

    deleted = cli("delete", "configmap", name)
    assert _rc(deleted) == 0
    assert f'"{name}"' in _out(deleted)
    assert "deleted" in _out(deleted)

    got_after = cli("get", "configmap", name)
    assert _rc(got_after) == 1
    assert "NotFound" in _err(got_after)


def test_create_is_not_idempotent_apply_is(cli, tmp_path):
    name = _uniq("cm2")
    manifest = f"""
apiVersion: v1
kind: ConfigMap
metadata:
  name: {name}
data:
  a: "1"
"""
    path = _write(tmp_path, "cm2.yaml", manifest)

    first_create = cli("create", "-f", path)
    assert _rc(first_create) == 0

    second_create = cli("create", "-f", path)
    assert _rc(second_create) == 1
    assert "AlreadyExists" in _err(second_create)

    cli("delete", "configmap", name)

    first_apply = cli("apply", "-f", path)
    assert _rc(first_apply) == 0
    assert "created" in _out(first_apply)

    second_apply = cli("apply", "-f", path)
    assert _rc(second_apply) == 0
    combined = _out(second_apply)
    assert ("unchanged" in combined) or ("configured" in combined)

    cli("delete", "configmap", name)


def test_delete_ignore_not_found_returns_zero(cli):
    missing_name = _uniq("nope")
    plain = cli("delete", "configmap", missing_name)
    assert _rc(plain) == 1
    assert "NotFound" in _err(plain)

    ignored = cli("delete", "configmap", missing_name, "--ignore-not-found")
    assert _rc(ignored) == 0


# ---------------------------------------------------------------------------
# Output-shape / machine-parseability contracts
# ---------------------------------------------------------------------------

def test_get_json_output_is_valid_json_matching_kind(cli, tmp_path):
    name = _uniq("cm3")
    manifest = f"""
apiVersion: v1
kind: ConfigMap
metadata:
  name: {name}
data:
  k: v
"""
    path = _write(tmp_path, "cm3.yaml", manifest)
    assert _rc(cli("create", "-f", path)) == 0

    result = cli("get", "configmap", name, "-o", "json")
    assert _rc(result) == 0
    parsed = json.loads(_out(result))
    assert parsed.get("kind") == "ConfigMap"
    assert parsed.get("metadata", {}).get("name") == name

    cli("delete", "configmap", name)


def test_describe_contains_required_sections(cli):
    result = cli("describe", "namespace", "default")
    assert _rc(result) == 0
    out = _out(result)
    assert "Name:" in out
    assert ("Status:" in out) or ("Labels:" in out)


# ---------------------------------------------------------------------------
# Mutating verbs persist state through the apiserver (label/scale)
# ---------------------------------------------------------------------------

def test_label_persists_across_invocations(cli, tmp_path):
    name = _uniq("cm4")
    manifest = f"""
apiVersion: v1
kind: ConfigMap
metadata:
  name: {name}
data:
  x: "y"
"""
    path = _write(tmp_path, "cm4.yaml", manifest)
    assert _rc(cli("create", "-f", path)) == 0

    labeled = cli("label", "configmap", name, "held-out-marker=abc123")
    assert _rc(labeled) == 0
    assert "labeled" in _out(labeled)

    got = cli("get", "configmap", name, "-o", "json")
    assert _rc(got) == 0
    parsed = json.loads(_out(got))
    labels = parsed.get("metadata", {}).get("labels", {}) or {}
    assert labels.get("held-out-marker") == "abc123"

    cli("delete", "configmap", name)


def test_scale_persists_replica_count(cli, tmp_path):
    name = _uniq("rs")
    manifest = f"""
apiVersion: apps/v1
kind: ReplicaSet
metadata:
  name: {name}
spec:
  replicas: 1
  selector:
    matchLabels:
      app: {name}
  template:
    metadata:
      labels:
        app: {name}
    spec:
      containers:
      - name: c
        image: busybox
"""
    path = _write(tmp_path, "rs.yaml", manifest)
    created = cli("create", "-f", path)
    assert _rc(created) == 0

    scaled = cli("scale", "replicaset", name, "--replicas=3")
    assert _rc(scaled) == 0
    assert "scaled" in _out(scaled)

    time.sleep(0.2)
    got = cli("get", "replicaset", name, "-o", "json")
    assert _rc(got) == 0
    parsed = json.loads(_out(got))
    assert parsed.get("spec", {}).get("replicas") == 3

    cli("delete", "replicaset", name)