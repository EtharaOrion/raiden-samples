"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

"""Held-out behavioral tests for the verb-first kubectl CLI submission.

These tests exercise cross-command state consistency, output-shape
contracts, and exit-code/error-path behavior described in TRUTH.md.
They do not hardcode any expected values beyond the documented contract.
"""

import json
import time
import uuid

import pytest


def _run(cli, *args):
    """Call the cli fixture regardless of whether it expects varargs or a list.

    Returns an object exposing .returncode, .stdout, .stderr (str).
    """
    try:
        result = cli(*args)
    except TypeError:
        result = cli(list(args))
    return result


def _unique_name(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _write_manifest(tmp_path, kind, name, namespace="default", extra_spec=None, filename=None):
    body = {
        "apiVersion": "v1",
        "kind": kind,
        "metadata": {"name": name, "namespace": namespace},
    }
    if extra_spec is not None:
        body["spec"] = extra_spec
    if kind == "ConfigMap":
        body.pop("spec", None)
        body["data"] = {"key": "value"}
    path = tmp_path / (filename or f"{name}.yaml")
    # minimal hand-rolled YAML emission (flat, known-shape) to avoid extra deps
    lines = [f"apiVersion: {body['apiVersion']}", f"kind: {body['kind']}", "metadata:"]
    lines.append(f"  name: {body['metadata']['name']}")
    if "namespace" in body["metadata"]:
        lines.append(f"  namespace: {body['metadata']['namespace']}")
    if "data" in body:
        lines.append("data:")
        for k, v in body["data"].items():
            lines.append(f"  {k}: {v}")
    if "spec" in body:
        lines.append("spec:")
        for k, v in body["spec"].items():
            lines.append(f"  {k}: {v}")
    path.write_text("\n".join(lines) + "\n")
    return path


def test_no_verb_given_exits_nonzero_error_path(cli):
    """Invoking with no verb at all must be a semantic error (exit 1 per contract)."""
    result = _run(cli)
    assert result.returncode != 0


def test_unknown_flag_exits_2_with_invalid_in_stderr(cli):
    result = _run(cli, "get", "pods", "--bogus-flag-xyz")
    assert result.returncode == 2
    assert "invalid" in (result.stderr or "").lower()


def test_delete_missing_name_and_missing_all_exits_2(cli):
    result = _run(cli, "delete", "pod")
    assert result.returncode == 2


def test_describe_missing_positional_name_is_error(cli):
    result = _run(cli, "describe", "pod")
    assert result.returncode in (1, 2)


def test_create_then_get_roundtrip_configmap(cli, tmp_path):
    name = _unique_name("cm")
    manifest = _write_manifest(tmp_path, "ConfigMap", name)
    create_res = _run(cli, "create", "-f", str(manifest))
    assert create_res.returncode == 0
    assert "created" in create_res.stdout

    get_res = _run(cli, "get", "configmap", name, "-n", "default")
    assert get_res.returncode == 0
    assert name in get_res.stdout

    # cleanup
    _run(cli, "delete", "configmap", name, "-n", "default", "--ignore-not-found")


def test_create_is_not_idempotent_second_call_conflicts(cli, tmp_path):
    name = _unique_name("cm2")
    manifest = _write_manifest(tmp_path, "ConfigMap", name)
    first = _run(cli, "create", "-f", str(manifest))
    assert first.returncode == 0

    second = _run(cli, "create", "-f", str(manifest))
    assert second.returncode == 1
    combined = (second.stdout or "") + (second.stderr or "")
    assert "AlreadyExists" in combined

    _run(cli, "delete", "configmap", name, "-n", "default", "--ignore-not-found")


def test_apply_is_idempotent_unchanged_on_repeat(cli, tmp_path):
    name = _unique_name("cm3")
    manifest = _write_manifest(tmp_path, "ConfigMap", name)
    first = _run(cli, "apply", "-f", str(manifest))
    assert first.returncode == 0
    assert "created" in first.stdout

    second = _run(cli, "apply", "-f", str(manifest))
    assert second.returncode == 0
    assert ("configured" in second.stdout) or ("unchanged" in second.stdout)

    _run(cli, "delete", "configmap", name, "-n", "default", "--ignore-not-found")


def test_delete_then_get_returns_notfound(cli, tmp_path):
    name = _unique_name("cm4")
    manifest = _write_manifest(tmp_path, "ConfigMap", name)
    _run(cli, "create", "-f", str(manifest))

    del_res = _run(cli, "delete", "configmap", name, "-n", "default")
    assert del_res.returncode == 0
    assert f'"{name}"' in del_res.stdout
    assert "deleted" in del_res.stdout

    get_res = _run(cli, "get", "configmap", name, "-n", "default")
    assert get_res.returncode == 1
    combined = (get_res.stdout or "") + (get_res.stderr or "")
    assert ("NotFound" in combined) or ("not found" in combined)


def test_delete_nonexistent_with_ignore_not_found_exits_0(cli):
    name = _unique_name("ghost")
    result = _run(cli, "delete", "configmap", name, "-n", "default", "--ignore-not-found")
    assert result.returncode == 0


def test_delete_nonexistent_without_ignore_flag_exits_1(cli):
    name = _unique_name("ghost2")
    result = _run(cli, "delete", "configmap", name, "-n", "default")
    assert result.returncode == 1
    combined = (result.stdout or "") + (result.stderr or "")
    assert ("NotFound" in combined) or ("not found" in combined)


def test_label_mutation_visible_on_subsequent_get(cli, tmp_path):
    name = _unique_name("cm5")
    manifest = _write_manifest(tmp_path, "ConfigMap", name)
    create_res = _run(cli, "create", "-f", str(manifest))
    assert create_res.returncode == 0

    label_res = _run(cli, "label", "configmap", name, "-n", "default", "team=platform")
    assert label_res.returncode == 0

    get_res = _run(cli, "get", "configmap", name, "-n", "default", "-o", "json")
    assert get_res.returncode == 0
    try:
        obj = json.loads(get_res.stdout)
        labels = obj.get("metadata", {}).get("labels", {}) or {}
        assert labels.get("team") == "platform"
    except json.JSONDecodeError:
        # if -o json unsupported for this path, at least the label value
        # should surface somewhere in a describe/get rendering
        describe_res = _run(cli, "describe", "configmap", name, "-n", "default")
        assert "team=platform" in describe_res.stdout or "team" in describe_res.stdout

    _run(cli, "delete", "configmap", name, "-n", "default", "--ignore-not-found")


def test_namespace_is_cluster_scoped_and_roundtrips(cli):
    name = _unique_name("ns")
    create_res = _run(cli, "create", "namespace", name)
    assert create_res.returncode == 0
    assert "created" in create_res.stdout

    get_res = _run(cli, "get", "namespace", name)
    assert get_res.returncode == 0
    assert name in get_res.stdout

    describe_res = _run(cli, "describe", "namespace", name)
    assert describe_res.returncode == 0
    assert "Name:" in describe_res.stdout

    del_res = _run(cli, "delete", "namespace", name)
    assert del_res.returncode == 0
    assert "deleted" in del_res.stdout