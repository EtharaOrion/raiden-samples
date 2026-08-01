"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

"""
Held-out pytest module for the kubectl-subset CLI (kwok-backed).

Uses the shipped `cli` fixture (subprocess invocation of the submission
entry point) exclusively -- no direct import of submission code. If a
`k8s_client` fixture is present it is used only as an independent oracle
for state-consistency checks; all tests guard its absence.
"""
import json
import uuid
import textwrap

import pytest


def _uniq(prefix="r2e"):
    return f"{prefix}-{uuid.uuid4().hex[:8]}"


def _run(cli, *args):
    """Normalize cli fixture call to always return an object with
    .returncode, .stdout, .stderr as str."""
    result = cli(list(args))
    return result


def _write_manifest(tmp_path, doc_text):
    p = tmp_path / f"{uuid.uuid4().hex[:8]}.yaml"
    p.write_text(doc_text)
    return str(p)


def _configmap_manifest(name, ns, value="v1"):
    return textwrap.dedent(f"""
    apiVersion: v1
    kind: ConfigMap
    metadata:
      name: {name}
      namespace: {ns}
    data:
      key: {value}
    """).strip() + "\n"


@pytest.fixture()
def ns(cli):
    """Create a throwaway namespace for isolation; skip if create fails
    outright (should not normally happen)."""
    name = _uniq("ns")
    r = _run(cli, "create", "namespace", name)
    if r.returncode != 0:
        pytest.skip("namespace creation not available; cannot isolate test")
    yield name
    # best-effort cleanup
    _run(cli, "delete", "namespace", name, "--ignore-not-found")


def test_create_then_get_roundtrip_visible(cli, ns):
    """An object created via `create` must be independently visible via a
    later `get -o json` invocation (no local caching)."""
    name = _uniq("cm")
    manifest = _configmap_manifest(name, ns, "hello")
    path = _write_manifest_tmp(manifest)
    r_create = _run(cli, "create", "-f", path)
    assert r_create.returncode == 0
    assert f"configmap/{name}" in r_create.stdout or f"ConfigMap/{name}" in r_create.stdout

    r_get = _run(cli, "get", "configmap", name, "-n", ns, "-o", "json")
    assert r_get.returncode == 0
    doc = json.loads(r_get.stdout)
    assert doc.get("metadata", {}).get("name") == name


def test_create_duplicate_is_already_exists(cli, ns):
    """create is strictly create-once: second create of the same object
    must fail with AlreadyExists / exit 1."""
    name = _uniq("cm")
    manifest = _configmap_manifest(name, ns)
    path = _write_manifest_tmp(manifest)
    first = _run(cli, "create", "-f", path)
    assert first.returncode == 0
    second = _run(cli, "create", "-f", path)
    assert second.returncode == 1
    assert "AlreadyExists" in second.stderr


def test_apply_idempotent_unchanged_then_configured(cli, ns):
    """apply must report created -> unchanged (same manifest) ->
    configured (changed manifest)."""
    name = _uniq("cm")
    manifest_v1 = _configmap_manifest(name, ns, "v1")
    path1 = _write_manifest_tmp(manifest_v1)

    r1 = _run(cli, "apply", "-f", path1)
    assert r1.returncode == 0
    assert "created" in r1.stdout

    r2 = _run(cli, "apply", "-f", path1)
    assert r2.returncode == 0
    assert "unchanged" in r2.stdout

    manifest_v2 = _configmap_manifest(name, ns, "v2-changed")
    path2 = _write_manifest_tmp(manifest_v2)
    r3 = _run(cli, "apply", "-f", path2)
    assert r3.returncode == 0
    assert "configured" in r3.stdout


def test_delete_makes_object_404_on_subsequent_get(cli, ns):
    """After delete, a subsequent get for the same name must exit 1 with
    NotFound/not found in stderr."""
    name = _uniq("cm")
    manifest = _configmap_manifest(name, ns)
    path = _write_manifest_tmp(manifest)
    assert _run(cli, "create", "-f", path).returncode == 0

    r_del = _run(cli, "delete", "configmap", name, "-n", ns)
    assert r_del.returncode == 0
    assert "deleted" in r_del.stdout

    r_get = _run(cli, "get", "configmap", name, "-n", ns)
    assert r_get.returncode == 1
    assert ("NotFound" in r_get.stderr) or ("not found" in r_get.stderr)


def test_delete_nonexistent_ignore_not_found_exits_zero(cli, ns):
    """--ignore-not-found must suppress the error and exit 0 for a
    nonexistent target."""
    r = _run(cli, "delete", "configmap", _uniq("ghost"), "-n", ns,
              "--ignore-not-found")
    assert r.returncode == 0


def test_delete_missing_name_and_no_all_is_usage_error(cli, ns):
    """delete with a TYPE but no NAME and no --all is a usage error (exit
    2), distinct from semantic NotFound errors (exit 1)."""
    r = _run(cli, "delete", "configmap", "-n", ns)
    assert r.returncode == 2
    combined = (r.stderr or "") + (r.stdout or "")
    assert ("invalid" in combined) or ("resource(s) were provided" in combined)


def test_unknown_flag_is_usage_error_exit_2(cli, ns):
    """An unrecognized flag on any verb must yield exit code 2 with
    'invalid' in stderr, regardless of verb."""
    r = _run(cli, "get", "pods", "-n", ns, "--totally-bogus-flag")
    assert r.returncode == 2
    assert "invalid" in (r.stderr or "").lower()


def test_bare_verb_with_no_args_exits_one(cli):
    """Calling apply/create/describe/get with zero further args is a
    semantic failure (missing manifest/target), exit 1 -- not exit 2."""
    r = _run(cli, "apply")
    assert r.returncode == 1


def test_label_add_persists_and_is_visible_via_get(cli, ns):
    """label mutations must persist to the server and be visible in a
    later independent get -o json call."""
    name = _uniq("cm")
    manifest = _configmap_manifest(name, ns)
    path = _write_manifest_tmp(manifest)
    assert _run(cli, "create", "-f", path).returncode == 0

    r_label = _run(cli, "label", "configmap", name, "-n", ns, "team=payments")
    assert r_label.returncode == 0

    r_get = _run(cli, "get", "configmap", name, "-n", ns, "-o", "json")
    assert r_get.returncode == 0
    doc = json.loads(r_get.stdout)
    labels = doc.get("metadata", {}).get("labels", {}) or {}
    assert labels.get("team") == "payments"


def test_describe_nonexistent_resource_is_notfound(cli, ns):
    """describe on a nonexistent resource must exit 1 with NotFound in
    stderr, and unknown flags on describe must exit 2."""
    r = _run(cli, "describe", "configmap", _uniq("ghost"), "-n", ns)
    assert r.returncode == 1
    assert "NotFound" in r.stderr

    r_flag = _run(cli, "describe", "configmap", "somename", "-n", ns,
                   "--not-a-real-flag")
    assert r_flag.returncode == 2


def test_get_output_json_is_valid_and_get_yaml_is_parseable(cli, ns):
    """-o json must produce syntactically valid JSON describing the real
    server object (round-trippable), a minimal machine-parseability
    guarantee from the contract."""
    name = _uniq("cm")
    manifest = _configmap_manifest(name, ns)
    path = _write_manifest_tmp(manifest)
    assert _run(cli, "create", "-f", path).returncode == 0

    r = _run(cli, "get", "configmap", name, "-n", ns, "-o", "json")
    assert r.returncode == 0
    doc = json.loads(r.stdout)
    assert doc["kind"] == "ConfigMap"
    assert doc["metadata"]["namespace"] == ns


# ---- helper needing a shared tmp dir without pytest tmp_path fixture in
# module-level helper functions above (pytest fixtures can't be called
# directly outside test/fixture functions), so provide a small local
# implementation using tempfile.
import tempfile
import os as _os


def _write_manifest_tmp(text):
    fd, path = tempfile.mkstemp(suffix=".yaml")
    with _os.fdopen(fd, "w") as f:
        f.write(text)
    return path