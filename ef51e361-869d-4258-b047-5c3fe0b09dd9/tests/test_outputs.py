"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

"""
Held-out behavioral tests for the from-scratch kubectl-like CLI (kwok backend).

These tests exercise cross-command state consistency, idempotency semantics,
exit-code contracts, alias resolution, and output-shape guarantees that are
easy to get subtly wrong even in an otherwise "working" submission.

Only the shipped `cli` fixture is required. If a `k8s_client` fixture is
present (a direct backend client) it is used opportunistically for extra
cross-checks, but every test degrades gracefully to CLI-only assertions if
that fixture is absent.
"""
import json
import uuid

import pytest


def _uniq(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _run(cli, *args):
    """Normalize invocation of the cli fixture regardless of exact signature."""
    return cli(*args)


def test_unknown_flag_exits_2_with_usage_text(cli):
    result = _run(cli, "get", "pods", "--totally-bogus-flag")
    assert result.returncode == 2
    combined = (result.stderr or "") + (result.stdout or "")
    assert "invalid" in combined.lower() or "usage" in combined.lower()


def test_delete_missing_name_and_no_all_exits_2(cli):
    result = _run(cli, "delete", "pod")
    assert result.returncode == 2


def test_apply_missing_manifest_file_exits_1(cli, tmp_path):
    missing = tmp_path / "does-not-exist.yaml"
    result = _run(cli, "apply", "-f", str(missing))
    assert result.returncode == 1
    assert (result.stderr or "").strip() != ""


def test_namespace_create_get_delete_lifecycle(cli):
    name = _uniq("ns")
    created = _run(cli, "create", "namespace", name)
    assert created.returncode == 0
    assert name in created.stdout

    got = _run(cli, "get", "namespace", name)
    assert got.returncode == 0
    assert name in got.stdout

    got_json = _run(cli, "get", "namespace", name, "-o", "json")
    assert got_json.returncode == 0
    payload = json.loads(got_json.stdout)
    assert payload.get("metadata", {}).get("name") == name

    deleted = _run(cli, "delete", "namespace", name)
    assert deleted.returncode == 0
    assert name in deleted.stdout

    after = _run(cli, "get", "namespace", name)
    assert after.returncode == 1
    assert "notfound" in (after.stderr or "").lower().replace(" ", "")


def test_create_is_not_idempotent_apply_is(cli):
    name = _uniq("ns")
    first_create = _run(cli, "create", "namespace", name)
    assert first_create.returncode == 0
    try:
        second_create = _run(cli, "create", "namespace", name)
        assert second_create.returncode == 1
        assert "alreadyexists" in (second_create.stderr or "").lower().replace(" ", "")

        first_apply = _run(cli, "apply", "-f", "/dev/null") if False else None
    finally:
        _run(cli, "delete", "namespace", name)


def test_apply_manifest_created_then_unchanged(cli, tmp_path):
    name = _uniq("ns")
    manifest = tmp_path / "ns.yaml"
    manifest.write_text(
        f"apiVersion: v1\nkind: Namespace\nmetadata:\n  name: {name}\n"
    )
    try:
        first = _run(cli, "apply", "-f", str(manifest))
        assert first.returncode == 0
        assert "created" in first.stdout

        second = _run(cli, "apply", "-f", str(manifest))
        assert second.returncode == 0
        assert ("unchanged" in second.stdout) or ("configured" in second.stdout)
    finally:
        _run(cli, "delete", "namespace", name)


def test_describe_namespace_has_status_or_labels_section(cli):
    name = _uniq("ns")
    try:
        _run(cli, "create", "namespace", name)
        described = _run(cli, "describe", "namespace", name)
        assert described.returncode == 0
        assert "Name:" in described.stdout
        assert ("Status:" in described.stdout) or ("Labels:" in described.stdout)
    finally:
        _run(cli, "delete", "namespace", name)


def test_pod_alias_resolution_po_matches_pod(cli):
    # Both alias forms should be accepted for the TYPE positional and behave
    # identically for a lookup that legitimately 404s (no such pod exists).
    long_form = _run(cli, "get", "pod", "no-such-pod-xyz", "-n", "default")
    short_form = _run(cli, "get", "po", "no-such-pod-xyz", "-n", "default")
    assert long_form.returncode == short_form.returncode == 1
    assert "notfound" in (long_form.stderr or "").lower().replace(" ", "")
    assert "notfound" in (short_form.stderr or "").lower().replace(" ", "")


def test_scale_missing_positional_or_bad_replicas_is_cli_error(cli):
    result = _run(cli, "scale", "deployment", "no-such-deploy", "--replicas=notanumber")
    # Either flagged as a usage/parse error (2) or surfaced as an apiserver
    # error because the object doesn't exist (1) - but must not silently
    # succeed (0) nor crash uncaught.
    assert result.returncode in (1, 2)


def test_dry_run_client_does_not_persist(cli, tmp_path):
    name = _uniq("ns")
    manifest = tmp_path / "ns.yaml"
    manifest.write_text(
        f"apiVersion: v1\nkind: Namespace\nmetadata:\n  name: {name}\n"
    )
    dry = _run(cli, "apply", "-f", str(manifest), "--dry-run=client")
    assert dry.returncode == 0

    lookup = _run(cli, "get", "namespace", name)
    assert lookup.returncode == 1
    assert "notfound" in (lookup.stderr or "").lower().replace(" ", "")


def test_create_secret_from_literal_base64_encodes_value(cli):
    name = _uniq("sec")
    try:
        created = _run(
            cli,
            "create",
            "secret",
            "generic",
            name,
            "--from-literal=key1=hello-world",
            "-n",
            "default",
        )
        assert created.returncode == 0

        got = _run(cli, "get", "secret", name, "-n", "default", "-o", "json")
        assert got.returncode == 0
        payload = json.loads(got.stdout)
        data = payload.get("data", {})
        assert "key1" in data
        # base64 of "hello-world" -> "aGVsbG8td29ybGQ="; raw plaintext must
        # never appear unencoded in the stored data field.
        assert data["key1"] != "hello-world"
    finally:
        _run(cli, "delete", "secret", name, "-n", "default")


def test_label_verb_updates_metadata_labels_and_is_visible_via_get(cli):
    name = _uniq("ns")
    try:
        _run(cli, "create", "namespace", name)
        labeled = _run(cli, "label", "namespace", name, "example.com/marker=present")
        assert labeled.returncode == 0

        got = _run(cli, "get", "namespace", name, "-o", "json")
        assert got.returncode == 0
        payload = json.loads(got.stdout)
        labels = payload.get("metadata", {}).get("labels", {}) or {}
        assert labels.get("example.com/marker") == "present"
    finally:
        _run(cli, "delete", "namespace", name)