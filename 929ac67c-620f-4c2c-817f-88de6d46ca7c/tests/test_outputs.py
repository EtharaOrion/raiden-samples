"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

"""
Held-out pytest module for the verb-first kubectl-subset CLI (kwok-backed).

These tests exercise cross-command state consistency, output-shape and
error-path contracts described in TRUTH.md, without hardcoding the exact
wording of success/error messages beyond the substrings the contract
guarantees.
"""

import json
import time
import uuid

import pytest
import yaml


def _uniq(prefix="t"):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _write_manifest(tmp_path, obj, name="manifest.yaml"):
    path = tmp_path / name
    path.write_text(yaml.safe_dump(obj))
    return str(path)


def _configmap(name, ns="default", data=None):
    return {
        "apiVersion": "v1",
        "kind": "ConfigMap",
        "metadata": {"name": name, "namespace": ns},
        "data": data or {"foo": "bar"},
    }


def _deployment(name, ns="default", replicas=1, image="nginx:latest"):
    return {
        "apiVersion": "apps/v1",
        "kind": "Deployment",
        "metadata": {"name": name, "namespace": ns},
        "spec": {
            "replicas": replicas,
            "selector": {"matchLabels": {"app": name}},
            "template": {
                "metadata": {"labels": {"app": name}},
                "spec": {"containers": [{"name": "c", "image": image}]},
            },
        },
    }


# --------------------------------------------------------------------------
# create -> get round trip and AlreadyExists on duplicate create
# --------------------------------------------------------------------------

def test_create_then_get_visible(cli, tmp_path):
    name = _uniq("cm")
    manifest = _write_manifest(tmp_path, _configmap(name))

    res = cli("create", "-f", manifest)
    assert res.returncode == 0, res.stderr
    assert f"configmap/{name}" in res.stdout or name in res.stdout

    got = cli("get", "configmap", name, "-n", "default")
    assert got.returncode == 0
    assert name in got.stdout


def test_create_duplicate_is_not_idempotent(cli, tmp_path):
    name = _uniq("cm")
    manifest = _write_manifest(tmp_path, _configmap(name))

    first = cli("create", "-f", manifest)
    assert first.returncode == 0

    second = cli("create", "-f", manifest)
    assert second.returncode == 1
    assert "AlreadyExists" in second.stderr


# --------------------------------------------------------------------------
# apply idempotency: created -> unchanged
# --------------------------------------------------------------------------

def test_apply_idempotent_created_then_unchanged(cli, tmp_path):
    name = _uniq("cm")
    manifest = _write_manifest(tmp_path, _configmap(name, data={"k": "v"}))

    first = cli("apply", "-f", manifest)
    assert first.returncode == 0
    assert "created" in first.stdout

    second = cli("apply", "-f", manifest)
    assert second.returncode == 0
    assert "unchanged" in second.stdout or "configured" in second.stdout


# --------------------------------------------------------------------------
# delete -> subsequent get 404s
# --------------------------------------------------------------------------

def test_delete_then_get_not_found(cli, tmp_path):
    name = _uniq("cm")
    manifest = _write_manifest(tmp_path, _configmap(name))
    assert cli("create", "-f", manifest).returncode == 0

    deleted = cli("delete", "configmap", name, "-n", "default")
    assert deleted.returncode == 0
    assert "deleted" in deleted.stdout

    after = cli("get", "configmap", name, "-n", "default")
    assert after.returncode == 1
    assert "NotFound" in after.stderr or "not found" in after.stderr


def test_delete_ignore_not_found_is_success(cli):
    name = _uniq("cm")
    res = cli("delete", "configmap", name, "-n", "default", "--ignore-not-found")
    assert res.returncode == 0


# --------------------------------------------------------------------------
# argparse-style flag errors vs usage errors
# --------------------------------------------------------------------------

def test_unrecognized_flag_exit_code_2(cli):
    res = cli("get", "pods", "--bogus-flag-xyz")
    assert res.returncode == 2


def test_delete_missing_target_without_all_exit_2(cli):
    res = cli("delete", "pod")
    assert res.returncode == 2


# --------------------------------------------------------------------------
# unknown kind must error, not silently succeed
# --------------------------------------------------------------------------

def test_unknown_kind_describe_fails(cli):
    res = cli("describe", "totallynotakind", "whatever")
    assert res.returncode == 1


# --------------------------------------------------------------------------
# scale reflected in get, across verbs
# --------------------------------------------------------------------------

def test_scale_deployment_reflected_in_get(cli, tmp_path):
    name = _uniq("dep")
    manifest = _write_manifest(tmp_path, _deployment(name, replicas=1))
    assert cli("create", "-f", manifest).returncode == 0

    scaled = cli("scale", "deployment", name, "--replicas=3", "-n", "default")
    assert scaled.returncode == 0

    got = cli("get", "deployment", name, "-n", "default", "-o", "json")
    assert got.returncode == 0
    obj = json.loads(got.stdout)
    assert obj["spec"]["replicas"] == 3


# --------------------------------------------------------------------------
# label add/remove mutation visible afterward
# --------------------------------------------------------------------------

def test_label_add_visible_via_get_json(cli, tmp_path):
    name = _uniq("cm")
    manifest = _write_manifest(tmp_path, _configmap(name))
    assert cli("create", "-f", manifest).returncode == 0

    labeled = cli("label", "configmap", name, "team=platform", "-n", "default")
    assert labeled.returncode == 0

    got = cli("get", "configmap", name, "-n", "default", "-o", "json")
    assert got.returncode == 0
    obj = json.loads(got.stdout)
    labels = obj.get("metadata", {}).get("labels", {}) or {}
    assert labels.get("team") == "platform"


# --------------------------------------------------------------------------
# get -o json output must be genuinely parseable and reflect live state
# --------------------------------------------------------------------------

def test_get_json_output_is_valid_and_matches_name(cli, tmp_path):
    name = _uniq("cm")
    manifest = _write_manifest(tmp_path, _configmap(name, data={"a": "1"}))
    assert cli("create", "-f", manifest).returncode == 0

    got = cli("get", "configmap", name, "-n", "default", "-o", "json")
    assert got.returncode == 0
    obj = json.loads(got.stdout)
    assert obj["metadata"]["name"] == name
    assert obj["data"]["a"] == "1"


# --------------------------------------------------------------------------
# namespace default handling
# --------------------------------------------------------------------------

def test_namespace_defaults_to_default_namespace(cli, tmp_path):
    name = _uniq("cm")
    # manifest omits namespace entirely
    obj = _configmap(name)
    del obj["metadata"]["namespace"]
    manifest = _write_manifest(tmp_path, obj)
    assert cli("create", "-f", manifest).returncode == 0

    got_default = cli("get", "configmap", name, "-n", "default")
    assert got_default.returncode == 0
    assert name in got_default.stdout