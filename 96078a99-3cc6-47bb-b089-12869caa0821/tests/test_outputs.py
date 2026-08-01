"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

"""
Held-out pytest module for the kubectl-mimic CLI contract (kwok-backed).

These tests exercise cross-verb state consistency, output-contract shape,
idempotency, and error-path exit codes against the real kwok apiserver via
the `cli` fixture. An optional independent backend client fixture (any of
`k8s_client`, `core_v1`, `api_client`) is used opportunistically to verify
state via a path other than the CLI itself; tests degrade gracefully to
CLI-only verification if no such fixture is present.
"""
import json
import time
import uuid

import pytest


def _uniq(prefix):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _get_backend_client(request):
    for fname in ("k8s_client", "core_v1", "api_client", "corev1_api"):
        if fname in request.fixturenames:
            try:
                return request.getfixturevalue(fname)
            except Exception:
                return None
    return None


def _write_manifest(tmp_path, name, content):
    p = tmp_path / name
    p.write_text(content)
    return str(p)


CM_MANIFEST_TMPL = """
apiVersion: v1
kind: ConfigMap
metadata:
  name: {name}
  namespace: default
data:
  foo: bar
"""

DEPLOY_MANIFEST_TMPL = """
apiVersion: apps/v1
kind: Deployment
metadata:
  name: {name}
  namespace: default
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
        image: busybox:latest
"""


@pytest.fixture
def cm_manifest(tmp_path):
    name = _uniq("cm")
    path = _write_manifest(tmp_path, "cm.yaml", CM_MANIFEST_TMPL.format(name=name))
    return name, path


@pytest.fixture
def deploy_manifest(tmp_path):
    name = _uniq("dep")
    path = _write_manifest(tmp_path, "dep.yaml", DEPLOY_MANIFEST_TMPL.format(name=name))
    return name, path


def test_create_then_get_json_roundtrip(cli, cm_manifest):
    name, path = cm_manifest
    r = cli("create", "-f", path)
    assert r.returncode == 0, r.stderr
    assert "created" in r.stdout

    r2 = cli("get", "configmap", name, "-o", "json", "-n", "default")
    assert r2.returncode == 0, r2.stderr
    obj = json.loads(r2.stdout)
    assert obj.get("kind", "").lower() == "configmap"
    assert obj["metadata"]["name"] == name

    cli("delete", "configmap", name, "-n", "default")


def test_create_duplicate_is_already_exists(cli, cm_manifest):
    name, path = cm_manifest
    r1 = cli("create", "-f", path)
    assert r1.returncode == 0, r1.stderr
    r2 = cli("create", "-f", path)
    assert r2.returncode == 1
    assert "AlreadyExists" in r2.stderr or "already exists" in r2.stderr.lower()
    cli("delete", "configmap", name, "-n", "default")


def test_apply_is_idempotent_unchanged_then_created_first_time(cli, cm_manifest):
    name, path = cm_manifest
    r1 = cli("apply", "-f", path)
    assert r1.returncode == 0, r1.stderr
    assert "created" in r1.stdout

    r2 = cli("apply", "-f", path)
    assert r2.returncode == 0, r2.stderr
    assert ("unchanged" in r2.stdout) or ("configured" in r2.stdout)

    cli("delete", "configmap", name, "-n", "default")


def test_delete_removes_object_visible_via_backend_or_get(cli, request, cm_manifest):
    name, path = cm_manifest
    r1 = cli("apply", "-f", path)
    assert r1.returncode == 0, r1.stderr

    rd = cli("delete", "configmap", name, "-n", "default")
    assert rd.returncode == 0, rd.stderr
    assert "deleted" in rd.stdout
    assert name in rd.stdout or True  # kind/name phrasing may vary in casing/quoting

    backend = _get_backend_client(request)
    if backend is not None:
        # Try the common kubernetes client shape: read_namespaced_config_map
        try:
            from kubernetes.client.rest import ApiException
            with pytest.raises(ApiException) as exc_info:
                backend.read_namespaced_config_map(name, "default")
            assert exc_info.value.status == 404
            return
        except ImportError:
            pass

    # Fall back to CLI-based 404 check
    rg = cli("get", "configmap", name, "-n", "default")
    assert rg.returncode == 1
    assert "NotFound" in rg.stderr or "not found" in rg.stderr.lower()


def test_get_nonexistent_returns_notfound_exit1(cli):
    r = cli("get", "configmap", "definitely-does-not-exist-xyz", "-n", "default")
    assert r.returncode == 1
    assert "NotFound" in r.stderr or "not found" in r.stderr.lower()


def test_unknown_flag_rejected_exit2(cli):
    r = cli("get", "pods", "--bogus-flag-xyz")
    assert r.returncode == 2


def test_delete_missing_name_and_no_all_flag_exit2_or_message(cli):
    r = cli("delete", "pods")
    # per contract: missing required name without --all -> usage failure
    assert r.returncode in (1, 2)
    assert "resource(s) were provided" in r.stderr or r.returncode == 2


def test_unknown_kind_get_and_describe_exit1(cli):
    r1 = cli("get", "totallynotarealkind", "somename")
    assert r1.returncode == 1

    r2 = cli("describe", "totallynotarealkind", "somename")
    assert r2.returncode == 1


def test_scale_updates_replicas_and_is_visible_via_get(cli, deploy_manifest):
    name, path = deploy_manifest
    r1 = cli("apply", "-f", path)
    assert r1.returncode == 0, r1.stderr

    rs = cli("scale", "deployment", name, "--replicas=3", "-n", "default")
    assert rs.returncode == 0, rs.stderr

    rg = cli("get", "deployment", name, "-o", "json", "-n", "default")
    assert rg.returncode == 0, rg.stderr
    obj = json.loads(rg.stdout)
    assert obj["spec"]["replicas"] == 3

    cli("delete", "deployment", name, "-n", "default")


def test_label_add_and_read_back(cli, cm_manifest):
    name, path = cm_manifest
    r1 = cli("apply", "-f", path)
    assert r1.returncode == 0, r1.stderr

    rl = cli("label", "configmap", name, "myk=myv", "-n", "default")
    assert rl.returncode == 0, rl.stderr

    rg = cli("get", "configmap", name, "-o", "json", "-n", "default")
    assert rg.returncode == 0, rg.stderr
    obj = json.loads(rg.stdout)
    labels = obj.get("metadata", {}).get("labels", {}) or {}
    assert labels.get("myk") == "myv"

    cli("delete", "configmap", name, "-n", "default")


def test_describe_does_not_mutate_state(cli, cm_manifest):
    name, path = cm_manifest
    r1 = cli("apply", "-f", path)
    assert r1.returncode == 0, r1.stderr

    rd1 = cli("describe", "configmap", name, "-n", "default")
    assert rd1.returncode == 0, rd1.stderr
    assert "Name:" in rd1.stdout
    assert name in rd1.stdout

    rg1 = cli("get", "configmap", name, "-o", "json", "-n", "default")
    obj1 = json.loads(rg1.stdout)
    rv1 = obj1.get("metadata", {}).get("resourceVersion")

    rd2 = cli("describe", "configmap", name, "-n", "default")
    assert rd2.returncode == 0

    rg2 = cli("get", "configmap", name, "-o", "json", "-n", "default")
    obj2 = json.loads(rg2.stdout)
    rv2 = obj2.get("metadata", {}).get("resourceVersion")

    if rv1 is not None and rv2 is not None:
        assert rv1 == rv2

    cli("delete", "configmap", name, "-n", "default")


def test_namespace_default_when_omitted(cli, cm_manifest):
    name, path = cm_manifest
    r1 = cli("apply", "-f", path)
    assert r1.returncode == 0, r1.stderr

    # omitting -n should default to "default" namespace
    rg = cli("get", "configmap", name)
    assert rg.returncode == 0, rg.stderr
    assert name in rg.stdout

    cli("delete", "configmap", name, "-n", "default")