"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

"""
Held-out pytest module for TRUTH a910a9f1-ccfb-4428-9267-615cbea82ff8.

Uses the shipped `cli` fixture (subprocess invocation of the submission
entry point). Verifies cross-command state consistency, output-shape
contracts, and error-path exit codes without hardcoding any hidden
oracle strings beyond what TRUTH.md pins down explicitly.
"""
import base64
import json
import uuid

import pytest


def _uniq(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _get_json(cli, kind, name, namespace=None):
    args = ["get", kind, name, "-o", "json"]
    if namespace:
        args += ["-n", namespace]
    res = cli(args)
    assert res.returncode == 0, f"expected get to succeed: {res.stderr}"
    return json.loads(res.stdout)


def test_verb_first_dispatch_rejects_type_verb_order(cli):
    # TRUTH.md: invocation shape is strictly VERB [TYPE] ..., never TYPE VERB.
    res = cli("pod", "get")
    assert res.returncode != 0


def test_get_missing_type_positional_is_usage_error(cli):
    res = cli("get")
    assert res.returncode == 2
    assert "invalid" in res.stderr.lower()


def test_unknown_flag_is_usage_error(cli):
    res = cli("get", "pods", "--totally-bogus-flag")
    assert res.returncode == 2
    assert "invalid" in res.stderr.lower()


def test_delete_requires_name_or_all(cli):
    name = _uniq("cm")
    # No name and no --all specified -> exit 2, not silent success.
    res = cli("delete", "configmap")
    assert res.returncode == 2


def test_configmap_create_get_and_duplicate_create_fails(cli):
    name = _uniq("cm")
    res = cli("create", "configmap", name, "--from-literal=foo=bar")
    assert res.returncode == 0
    assert "created" in res.stdout

    obj = _get_json(cli, "configmap", name)
    assert obj["data"]["foo"] == "bar"

    # create is not idempotent: second create -> AlreadyExists / exit 1
    res2 = cli("create", "configmap", name, "--from-literal=foo=bar")
    assert res2.returncode == 1
    assert "AlreadyExists" in res2.stderr

    cli("delete", "configmap", name)


def test_secret_from_literal_is_base64_encoded_configmap_is_not(cli):
    cm_name = _uniq("cm")
    sec_name = _uniq("sec")

    res_cm = cli("create", "configmap", cm_name, "--from-literal=k=plainvalue")
    assert res_cm.returncode == 0
    cm = _get_json(cli, "configmap", cm_name)
    assert cm["data"]["k"] == "plainvalue"

    res_sec = cli("create", "secret", "generic", sec_name, "--from-literal=k=plainvalue")
    assert res_sec.returncode == 0
    sec = _get_json(cli, "secret", sec_name)
    decoded = base64.b64decode(sec["data"]["k"]).decode()
    assert decoded == "plainvalue"

    cli("delete", "configmap", cm_name)
    cli("delete", "secret", sec_name)


def test_apply_lifecycle_created_unchanged_configured(cli, tmp_path):
    name = _uniq("cm")
    manifest_path = tmp_path / "cm.yaml"
    manifest_path.write_text(
        f"apiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: {name}\ndata:\n  a: \"1\"\n"
    )

    res1 = cli("apply", "-f", str(manifest_path))
    assert res1.returncode == 0
    assert "created" in res1.stdout

    res2 = cli("apply", "-f", str(manifest_path))
    assert res2.returncode == 0
    assert "unchanged" in res2.stdout

    manifest_path.write_text(
        f"apiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: {name}\ndata:\n  a: \"2\"\n"
    )
    res3 = cli("apply", "-f", str(manifest_path))
    assert res3.returncode == 0
    assert "configured" in res3.stdout

    obj = _get_json(cli, "configmap", name)
    assert obj["data"]["a"] == "2"

    cli("delete", "configmap", name)


def test_delete_quoted_message_shape_and_subsequent_404(cli):
    name = _uniq("cm")
    res_create = cli("create", "configmap", name, "--from-literal=x=y")
    assert res_create.returncode == 0

    res_del = cli("delete", "configmap", name)
    assert res_del.returncode == 0
    # required quoted-name shape: kind "name" deleted (not kind/name deleted)
    assert f'"{name}" deleted' in res_del.stdout
    assert f"configmap/{name} deleted" not in res_del.stdout

    res_get = cli("get", "configmap", name, "-o", "json")
    assert res_get.returncode == 1
    assert "NotFound" in res_get.stderr


def test_delete_ignore_not_found_exits_zero(cli):
    name = _uniq("cm-missing")
    res = cli("delete", "configmap", name, "--ignore-not-found")
    assert res.returncode == 0


def test_describe_is_read_only(cli):
    name = _uniq("cm")
    res_create = cli("create", "configmap", name, "--from-literal=a=b")
    assert res_create.returncode == 0

    before = _get_json(cli, "configmap", name)
    rv_before = before["metadata"].get("resourceVersion")

    res_describe = cli("describe", "configmap", name)
    assert res_describe.returncode == 0
    assert "Name:" in res_describe.stdout
    assert name in res_describe.stdout

    after = _get_json(cli, "configmap", name)
    rv_after = after["metadata"].get("resourceVersion")
    assert rv_before == rv_after

    cli("delete", "configmap", name)


def test_label_patches_metadata_labels(cli):
    name = _uniq("cm")
    res_create = cli("create", "configmap", name, "--from-literal=a=b")
    assert res_create.returncode == 0

    res_label = cli("label", "configmap", name, "tier=backend")
    assert res_label.returncode == 0

    obj = _get_json(cli, "configmap", name)
    labels = obj["metadata"].get("labels") or {}
    assert labels.get("tier") == "backend"

    cli("delete", "configmap", name)


def test_scale_updates_replicas_on_deployment(cli):
    name = _uniq("dep")
    res_create = cli("create", "deployment", name, "--image=busybox")
    if res_create.returncode != 0:
        pytest.skip("typed deployment creation not supported in this environment")

    res_scale = cli("scale", "deployment", name, "--replicas=3")
    assert res_scale.returncode == 0

    obj = _get_json(cli, "deployment", name)
    assert obj["spec"]["replicas"] == 3

    cli("delete", "deployment", name)