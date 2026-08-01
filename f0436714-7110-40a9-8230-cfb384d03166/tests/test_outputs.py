"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

"""
Held-out behavioral tests for the from-scratch kubectl reimplementation.

These tests exercise cross-command state consistency, idempotency,
exit-code contracts, and output-shape guarantees described in TRUTH.md.
They invoke the submission strictly as a subprocess via the shipped
`cli` fixture (never import the submission module directly).
"""
import json
import uuid
import textwrap

import pytest


def _rand_name(prefix="r2e"):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _write_manifest(tmp_path, text, fname="manifest.yaml"):
    p = tmp_path / fname
    p.write_text(textwrap.dedent(text))
    return str(p)


def _configmap_manifest(name, value="v1"):
    return f"""
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: {name}
    data:
      key: {value}
    """


def _deployment_manifest(name, replicas=1):
    return f"""
    apiVersion: apps/v1
    kind: Deployment
    metadata:
      name: {name}
    spec:
      replicas: {replicas}
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
            image: nginx:latest
    """


def test_create_then_create_again_is_not_idempotent(cli, tmp_path):
    name = _rand_name("cm")
    manifest = _write_manifest(tmp_path, _configmap_manifest(name))

    first = cli("create", "-f", manifest)
    assert first.returncode == 0
    assert f"configmap/{name}" in first.stdout or name in first.stdout

    second = cli("create", "-f", manifest)
    assert second.returncode == 1
    assert "AlreadyExists" in second.stderr

    # cleanup
    cli("delete", "configmap", name)


def test_apply_is_idempotent_unchanged_then_configured(cli, tmp_path):
    name = _rand_name("cm")
    manifest_v1 = _write_manifest(tmp_path, _configmap_manifest(name, "v1"), "m1.yaml")

    created = cli("apply", "-f", manifest_v1)
    assert created.returncode == 0
    assert "created" in created.stdout

    reapplied = cli("apply", "-f", manifest_v1)
    assert reapplied.returncode == 0
    assert "unchanged" in reapplied.stdout

    manifest_v2 = _write_manifest(tmp_path, _configmap_manifest(name, "v2"), "m2.yaml")
    changed = cli("apply", "-f", manifest_v2)
    assert changed.returncode == 0
    assert "configured" in changed.stdout

    cli("delete", "configmap", name)


def test_delete_missing_resource_ignore_not_found_exit0_vs_error_exit1(cli):
    name = _rand_name("ghost")

    without_flag = cli("delete", "pod", name)
    assert without_flag.returncode == 1
    assert "NotFound" in without_flag.stderr or "not found" in without_flag.stderr

    with_flag = cli("delete", "pod", name, "--ignore-not-found")
    assert with_flag.returncode == 0


def test_delete_without_name_or_all_is_usage_error(cli):
    result = cli("delete", "pod")
    assert result.returncode == 2
    assert "invalid" in result.stderr.lower()


def test_unknown_flag_is_usage_error_exit_2(cli):
    result = cli("get", "pods", "--bogus-flag-xyz")
    assert result.returncode == 2
    assert "invalid" in result.stderr.lower()


def test_state_consistency_create_get_patch_scale_delete_chain(cli, tmp_path):
    name = _rand_name("deploy")
    manifest = _write_manifest(tmp_path, _deployment_manifest(name, replicas=1))

    created = cli("create", "-f", manifest)
    assert created.returncode == 0

    got = cli("get", "deployment", name, "-o", "json")
    assert got.returncode == 0
    obj = json.loads(got.stdout)
    assert obj.get("metadata", {}).get("name") == name

    scaled = cli("scale", "deployment", name, "--replicas=3")
    assert scaled.returncode == 0

    got2 = cli("get", "deployment", name, "-o", "json")
    obj2 = json.loads(got2.stdout)
    assert obj2["spec"]["replicas"] == 3

    labeled = cli("label", "deployment", name, "team=platform")
    assert labeled.returncode == 0

    got3 = cli("get", "deployment", name, "-o", "json")
    obj3 = json.loads(got3.stdout)
    assert obj3.get("metadata", {}).get("labels", {}).get("team") == "platform"

    deleted = cli("delete", "deployment", name)
    assert deleted.returncode == 0
    assert f'"{name}"' in deleted.stdout

    after = cli("get", "deployment", name)
    assert after.returncode == 1
    assert "NotFound" in after.stderr or "not found" in after.stderr


def test_get_output_json_and_yaml_are_machine_parseable(cli, tmp_path):
    name = _rand_name("cm")
    manifest = _write_manifest(tmp_path, _configmap_manifest(name))
    created = cli("create", "-f", manifest)
    assert created.returncode == 0

    as_json = cli("get", "configmap", name, "-o", "json")
    assert as_json.returncode == 0
    parsed = json.loads(as_json.stdout)
    assert parsed["kind"] == "ConfigMap"
    assert parsed["metadata"]["name"] == name

    as_yaml = cli("get", "configmap", name, "-o", "yaml")
    assert as_yaml.returncode == 0
    import yaml as _yaml
    parsed_yaml = _yaml.safe_load(as_yaml.stdout)
    assert parsed_yaml["metadata"]["name"] == name

    cli("delete", "configmap", name)


def test_delete_message_shape_differs_from_apply_create(cli, tmp_path):
    name = _rand_name("cm")
    manifest = _write_manifest(tmp_path, _configmap_manifest(name))
    created = cli("create", "-f", manifest)
    assert created.returncode == 0
    assert f"configmap/{name} created" in created.stdout.lower().replace("Configmap", "configmap") or \
        f"/{name} created" in created.stdout

    deleted = cli("delete", "configmap", name)
    assert deleted.returncode == 0
    assert f'"{name}"' in deleted.stdout
    assert "deleted" in deleted.stdout
    # delete's message must not reuse the apply/create slash form
    assert f"/{name} deleted" not in deleted.stdout


def test_describe_namespace_contains_required_sections(cli):
    result = cli("describe", "namespace", "default")
    assert result.returncode == 0
    assert "Name:" in result.stdout
    assert ("Status:" in result.stdout) or ("Labels:" in result.stdout)


def test_namespace_default_scoping_and_explicit_override(cli, tmp_path):
    name = _rand_name("cm")
    manifest = _write_manifest(tmp_path, _configmap_manifest(name))

    created = cli("create", "-f", manifest)
    assert created.returncode == 0

    default_ns_get = cli("get", "configmap", name, "-n", "default")
    assert default_ns_get.returncode == 0

    # not present when queried under an unrelated (nonexistent-resource) namespace name
    # ensures namespace flag actually changes the lookup scope semantically
    other_ns_get = cli("get", "configmap", name, "-n", "kube-system")
    assert other_ns_get.returncode == 1
    assert "NotFound" in other_ns_get.stderr or "not found" in other_ns_get.stderr

    cli("delete", "configmap", name)


def test_invalid_manifest_file_missing_exits_1_with_invalid_substring(cli, tmp_path):
    missing_path = str(tmp_path / "does-not-exist.yaml")
    result = cli("apply", "-f", missing_path)
    assert result.returncode == 1
    assert "invalid" in result.stderr.lower()


def test_patch_verb_mutates_visible_state(cli, tmp_path):
    name = _rand_name("cm")
    manifest = _write_manifest(tmp_path, _configmap_manifest(name, "orig"))
    created = cli("create", "-f", manifest)
    assert created.returncode == 0

    patch_body = json.dumps({"data": {"key": "patched"}})
    patched = cli("patch", "configmap", name, "--type", "merge", "-p", patch_body)
    assert patched.returncode == 0

    got = cli("get", "configmap", name, "-o", "json")
    obj = json.loads(got.stdout)
    assert obj["data"]["key"] == "patched"

    cli("delete", "configmap", name)