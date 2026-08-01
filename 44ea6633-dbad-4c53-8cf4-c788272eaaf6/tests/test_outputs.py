"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

"""
Held-out pytest module for the kubectl-subset CLI (kwok-backed).

These tests exercise cross-verb state consistency, idempotency semantics,
exit-code contracts, and output-shape guarantees described in TRUTH.md.
They are intentionally independent of any specific implementation strategy
(raw REST vs generated client vs vendored kubectl wrapper) and only assert
externally observable behavior.
"""
import json
import uuid
import pytest


def _uniq(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _run(cli, args):
    """Normalize invocation across possible cli fixture call conventions."""
    return cli(args)


@pytest.fixture
def tmp_manifest(tmp_path):
    def _write(text):
        p = tmp_path / f"{uuid.uuid4().hex[:8]}.yaml"
        p.write_text(text)
        return str(p)
    return _write


def test_create_get_delete_lifecycle_is_real_and_observable(cli):
    name = _uniq("cm")
    created = _run(cli, ["create", "configmap", name, "--from-literal=foo=bar"])
    assert created.returncode == 0
    assert f"{name} created" in created.stdout or "configmap" in created.stdout.lower()

    got = _run(cli, ["get", "configmap", name, "-o", "json"])
    assert got.returncode == 0
    data = json.loads(got.stdout)
    assert data.get("metadata", {}).get("name") == name

    deleted = _run(cli, ["delete", "configmap", name])
    assert deleted.returncode == 0
    assert f'"{name}"' in deleted.stdout
    assert "deleted" in deleted.stdout

    after = _run(cli, ["get", "configmap", name])
    assert after.returncode == 1
    assert ("NotFound" in after.stderr) or ("not found" in after.stderr.lower())


def test_create_is_not_idempotent_second_call_conflicts(cli):
    name = _uniq("cm")
    first = _run(cli, ["create", "configmap", name, "--from-literal=k=v"])
    assert first.returncode == 0
    second = _run(cli, ["create", "configmap", name, "--from-literal=k=v"])
    assert second.returncode == 1
    assert "AlreadyExists" in second.stderr

    cleanup = _run(cli, ["delete", "configmap", name, "--ignore-not-found"])
    assert cleanup.returncode == 0


def test_apply_is_idempotent_across_repeated_invocations(cli, tmp_manifest):
    name = _uniq("cm")
    manifest = tmp_manifest(
        f"apiVersion: v1\nkind: ConfigMap\nmetadata:\n  name: {name}\ndata:\n  a: b\n"
    )
    first = _run(cli, ["apply", "-f", manifest])
    assert first.returncode == 0
    assert "created" in first.stdout

    second = _run(cli, ["apply", "-f", manifest])
    assert second.returncode == 0
    assert ("unchanged" in second.stdout) or ("configured" in second.stdout)

    third = _run(cli, ["apply", "-f", manifest])
    assert third.returncode == 0

    _run(cli, ["delete", "configmap", name, "--ignore-not-found"])


def test_delete_without_name_or_all_is_usage_error(cli):
    result = _run(cli, ["delete", "configmap"])
    assert result.returncode == 2
    assert "resource(s) were provided" in result.stderr


def test_unknown_kind_is_runtime_error_not_usage_error(cli):
    result = _run(cli, ["get", "invalidkind", "somename"])
    assert result.returncode == 1
    assert result.returncode != 2


def test_unrecognized_flag_is_usage_error(cli):
    result = _run(cli, ["get", "configmap", "--totally-bogus-flag-xyz"])
    assert result.returncode == 2
    assert "invalid" in result.stderr.lower()


def test_namespace_flag_short_and_long_forms_are_equivalent(cli):
    ns = _uniq("ns")
    ns_created = _run(cli, ["create", "namespace", ns])
    assert ns_created.returncode == 0

    name_a = _uniq("cm")
    name_b = _uniq("cm")
    r1 = _run(cli, ["create", "configmap", name_a, "-n", ns, "--from-literal=x=1"])
    r2 = _run(cli, ["create", "configmap", name_b, "--namespace", ns, "--from-literal=x=1"])
    assert r1.returncode == 0
    assert r2.returncode == 0

    got_a = _run(cli, ["get", "configmap", name_a, "-n", ns])
    got_b = _run(cli, ["get", "configmap", name_b, "--namespace", ns])
    assert got_a.returncode == 0
    assert got_b.returncode == 0

    _run(cli, ["delete", "namespace", ns, "--ignore-not-found"])


def test_secret_from_literal_is_base64_encoded_server_side(cli):
    name = _uniq("sec")
    plain_value = "supersecretvalue"
    created = _run(cli, ["create", "secret", "generic", name, f"--from-literal=key={plain_value}"])
    assert created.returncode == 0

    got = _run(cli, ["get", "secret", name, "-o", "json"])
    assert got.returncode == 0
    data = json.loads(got.stdout)
    stored = data.get("data", {}).get("key", "")
    assert stored != plain_value
    assert stored != ""

    _run(cli, ["delete", "secret", name, "--ignore-not-found"])


def test_label_patch_scale_sequence_reflects_live_apiserver_state(cli, tmp_manifest):
    name = _uniq("dep")
    manifest = tmp_manifest(
        "apiVersion: apps/v1\n"
        "kind: Deployment\n"
        f"metadata:\n  name: {name}\n"
        "spec:\n"
        "  replicas: 1\n"
        "  selector:\n"
        "    matchLabels:\n"
        "      app: demo\n"
        "  template:\n"
        "    metadata:\n"
        "      labels:\n"
        "        app: demo\n"
        "    spec:\n"
        "      containers:\n"
        "      - name: c\n"
        "        image: busybox\n"
    )
    created = _run(cli, ["apply", "-f", manifest])
    assert created.returncode == 0

    labeled = _run(cli, ["label", "deployment", name, "env=test", "--overwrite"])
    assert labeled.returncode == 0
    assert "labeled" in labeled.stdout

    scaled = _run(cli, ["scale", "deployment", name, "--replicas=3"])
    assert scaled.returncode == 0
    assert "scaled" in scaled.stdout

    got = _run(cli, ["get", "deployment", name, "-o", "json"])
    assert got.returncode == 0
    data = json.loads(got.stdout)
    assert data.get("spec", {}).get("replicas") == 3
    assert data.get("metadata", {}).get("labels", {}).get("env") == "test"

    _run(cli, ["delete", "deployment", name, "--ignore-not-found"])


def test_describe_does_not_mutate_state_and_has_required_sections(cli):
    first = _run(cli, ["describe", "namespace", "default"])
    assert first.returncode == 0
    assert "Name:" in first.stdout
    assert ("Status:" in first.stdout) or ("Labels:" in first.stdout)

    second = _run(cli, ["describe", "namespace", "default"])
    assert second.returncode == 0
    assert "Name:" in second.stdout


def test_missing_manifest_file_is_runtime_error(cli):
    result = _run(cli, ["apply", "-f", "/tmp/does-not-exist-xyz-12345.yaml"])
    assert result.returncode == 1


def test_delete_reports_short_or_qualified_kind_name(cli):
    name = _uniq("cm")
    created = _run(cli, ["create", "configmap", name, "--from-literal=a=b"])
    assert created.returncode == 0

    deleted = _run(cli, ["delete", "configmap", name])
    assert deleted.returncode == 0
    lowered = deleted.stdout.lower()
    assert "configmap" in lowered
    assert "deleted" in lowered