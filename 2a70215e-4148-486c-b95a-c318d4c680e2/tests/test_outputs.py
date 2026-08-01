"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

"""Held-out pytest module for kubectl-reimplementation TRUTH 2a70215e.

These tests exercise cross-process, server-backed state consistency and
verb-specific output/exit-code contracts that are not simple echoes of the
visible suite. They rely on the shipped `cli` fixture (subprocess invoker)
and, where available, the `kwok_cluster` fixture to ensure a live backend is
up. All resource names are randomized per test to avoid collisions.
"""
import json
import textwrap
import uuid

import pytest


def _uniq(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _run(cli, *args):
    """Call the cli fixture defensively regardless of exact calling convention."""
    try:
        return cli(*args)
    except TypeError:
        return cli(list(args))


@pytest.fixture(autouse=True)
def _require_cluster(request):
    # If a session-scoped kwok_cluster fixture exists, make sure it's active
    # so the CLI subprocess talks to a real apiserver via KUBECONFIG.
    if "kwok_cluster" in request.fixturenames:
        request.getfixturevalue("kwok_cluster")


def test_create_then_get_cross_process_state_consistency(cli, kwok_cluster=None):
    """Object created in one subprocess invocation must be visible in a
    separate subsequent invocation (no local/in-process caching)."""
    name = _uniq("cm")
    r = _run(cli, "create", "configmap", name, "--from-literal=foo=bar")
    assert r.returncode == 0
    assert f"configmap/{name}" in r.stdout
    assert "created" in r.stdout

    # Fresh subprocess call - must see server state, not local cache.
    r2 = _run(cli, "get", "configmap", name, "-o", "json")
    assert r2.returncode == 0
    obj = json.loads(r2.stdout)
    assert obj["metadata"]["name"] == name
    assert obj["data"]["foo"] == "bar"

    _run(cli, "delete", "configmap", name, "--ignore-not-found")


def test_secret_from_literal_is_base64_encoded(cli):
    name = _uniq("sec")
    r = _run(cli, "create", "secret", "generic", name, "--from-literal=password=hunter2")
    assert r.returncode == 0
    assert "created" in r.stdout

    r2 = _run(cli, "get", "secret", name, "-o", "json")
    assert r2.returncode == 0
    obj = json.loads(r2.stdout)
    import base64
    raw = obj["data"]["password"]
    decoded = base64.b64decode(raw).decode()
    assert decoded == "hunter2"

    _run(cli, "delete", "secret", name, "--ignore-not-found")


def test_create_is_not_idempotent_already_exists(cli):
    name = _uniq("cm2")
    r1 = _run(cli, "create", "configmap", name, "--from-literal=a=1")
    assert r1.returncode == 0
    r2 = _run(cli, "create", "configmap", name, "--from-literal=a=1")
    assert r2.returncode == 1
    assert "AlreadyExists" in r2.stderr

    _run(cli, "delete", "configmap", name, "--ignore-not-found")


def test_apply_idempotent_unchanged_then_configured(cli, tmp_path):
    name = _uniq("cm3")
    manifest = tmp_path / "cm.yaml"
    manifest.write_text(textwrap.dedent(f"""
        apiVersion: v1
        kind: ConfigMap
        metadata:
          name: {name}
        data:
          k: v1
    """))

    r1 = _run(cli, "apply", "-f", str(manifest))
    assert r1.returncode == 0
    assert "created" in r1.stdout

    r2 = _run(cli, "apply", "-f", str(manifest))
    assert r2.returncode == 0
    assert "unchanged" in r2.stdout

    manifest.write_text(textwrap.dedent(f"""
        apiVersion: v1
        kind: ConfigMap
        metadata:
          name: {name}
        data:
          k: v2
    """))
    r3 = _run(cli, "apply", "-f", str(manifest))
    assert r3.returncode == 0
    assert "configured" in r3.stdout

    _run(cli, "delete", "configmap", name, "--ignore-not-found")


def test_delete_missing_resource_notfound_vs_ignore_not_found(cli):
    name = _uniq("ghost")
    r1 = _run(cli, "delete", "configmap", name)
    assert r1.returncode == 1
    assert "NotFound" in r1.stderr or "not found" in r1.stderr

    r2 = _run(cli, "delete", "configmap", name, "--ignore-not-found")
    assert r2.returncode == 0


def test_delete_output_shape_quoted_name_no_slash(cli):
    name = _uniq("cm4")
    _run(cli, "create", "configmap", name, "--from-literal=x=1")
    r = _run(cli, "delete", "configmap", name)
    assert r.returncode == 0
    assert f'"{name}"' in r.stdout
    assert "deleted" in r.stdout
    assert f"/{name}" not in r.stdout


def test_scale_and_label_lifecycle_on_deployment(cli):
    name = _uniq("dep")
    r0 = _run(cli, "create", "deployment", name, "--image=nginx:latest")
    assert r0.returncode == 0
    assert "created" in r0.stdout

    r1 = _run(cli, "scale", "deployment", name, "--replicas=3")
    assert r1.returncode == 0
    assert f"deployment/{name}" in r1.stdout or name in r1.stdout
    assert "scaled" in r1.stdout

    r2 = _run(cli, "get", "deployment", name, "-o", "json")
    assert r2.returncode == 0
    obj = json.loads(r2.stdout)
    assert obj["spec"]["replicas"] == 3

    r3 = _run(cli, "label", "deployment", name, "team=platform")
    assert r3.returncode == 0
    assert "labeled" in r3.stdout

    r4 = _run(cli, "get", "deployment", name, "-o", "json")
    obj4 = json.loads(r4.stdout)
    assert obj4["metadata"]["labels"].get("team") == "platform"

    _run(cli, "delete", "deployment", name, "--ignore-not-found")


def test_get_unknown_flag_exit_code_two(cli):
    r = _run(cli, "get", "pods", "--not-a-real-flag")
    assert r.returncode == 2
    assert "invalid" in r.stderr.lower()


def test_delete_missing_name_and_no_all_exit_two(cli):
    r = _run(cli, "delete", "configmap")
    assert r.returncode == 2
    assert "invalid" in r.stderr.lower() or "usage" in r.stderr.lower()


def test_cluster_scoped_namespace_kind_routing(cli):
    name = _uniq("ns")
    r0 = _run(cli, "create", "namespace", name)
    assert r0.returncode == 0
    assert "created" in r0.stdout

    r1 = _run(cli, "get", "namespace", name, "-o", "json")
    assert r1.returncode == 0
    obj = json.loads(r1.stdout)
    assert obj["metadata"]["name"] == name
    # cluster-scoped: no namespace field pointing to itself
    assert "namespace" not in obj["metadata"] or obj["metadata"].get("namespace") in (None, "")

    r2 = _run(cli, "delete", "namespace", name)
    assert r2.returncode == 0
    assert f'"{name}"' in r2.stdout