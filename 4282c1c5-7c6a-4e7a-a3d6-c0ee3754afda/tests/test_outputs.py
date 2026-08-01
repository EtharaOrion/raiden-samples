"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

"""
Held-out behavioral tests for the from-scratch `aws s3` CLI.

These tests exercise cross-command state consistency, output contract
shape, and error-path behavior against a real MinIO backend, using the
`cli` (subprocess) and `s3_client` (independent backend) fixtures shipped
in conftest.py.
"""
import os
import re
import uuid

import pytest

SUCCESS_LINE_RE = re.compile(r"^[a-z][a-z_\-]*:\s+\S", re.MULTILINE)
ALLOWED_EXIT_CODES = {0, 1, 2, 252, 255}


def _bucket_name():
    return f"held-out-{uuid.uuid4().hex[:12]}"


def _require_s3_client(s3_client):
    if s3_client is None:
        pytest.skip("s3_client fixture not available")


@pytest.fixture
def bucket(s3_client):
    _require_s3_client(s3_client)
    name = _bucket_name()
    s3_client.create_bucket(Bucket=name)
    yield name


def test_cp_round_trip_local_to_s3_to_local(cli, bucket, tmp_path):
    src = tmp_path / "upload.bin"
    payload = os.urandom(4096)
    src.write_bytes(payload)

    up = cli("s3", "cp", str(src), f"s3://{bucket}/round/upload.bin")
    assert up.returncode == 0, up.stderr
    assert up.stderr == ""
    assert SUCCESS_LINE_RE.search(up.stdout)

    dest = tmp_path / "download.bin"
    down = cli("s3", "cp", f"s3://{bucket}/round/upload.bin", str(dest))
    assert down.returncode == 0, down.stderr
    assert down.stderr == ""
    assert SUCCESS_LINE_RE.search(down.stdout)

    assert dest.read_bytes() == payload


def test_ls_no_args_lists_owned_buckets(cli, bucket):
    result = cli("s3", "ls")
    assert result.returncode == 0
    assert result.stderr == ""
    assert bucket in result.stdout


def test_ls_empty_bucket_exit_zero_no_entries(cli, bucket):
    result = cli("s3", "ls", f"s3://{bucket}/")
    assert result.returncode == 0
    assert result.stderr == ""
    # no object keys reported for an empty bucket
    assert "PRE" not in result.stdout or result.stdout.strip() == ""


def test_ls_recursive_flattens_no_pre_lines(cli, bucket, tmp_path, s3_client):
    _require_s3_client(s3_client)
    for key in ("dir1/a.txt", "dir1/dir2/b.txt", "dir3/c.txt"):
        f = tmp_path / "src.txt"
        f.write_text("data")
        r = cli("s3", "cp", str(f), f"s3://{bucket}/{key}")
        assert r.returncode == 0, r.stderr

    result = cli("s3", "ls", f"s3://{bucket}/", "--recursive")
    assert result.returncode == 0
    assert result.stderr == ""
    assert "PRE" not in result.stdout
    assert "dir1/a.txt" in result.stdout
    assert "dir1/dir2/b.txt" in result.stdout


def test_mv_local_to_s3_deletes_source_on_success(cli, bucket, tmp_path):
    src = tmp_path / "move_me.txt"
    src.write_text("payload-to-move")

    result = cli("s3", "mv", str(src), f"s3://{bucket}/moved/move_me.txt")
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert SUCCESS_LINE_RE.search(result.stdout)
    assert not src.exists()

    # confirm destination is really present via an independent cp (download)
    dest = tmp_path / "back.txt"
    down = cli("s3", "cp", f"s3://{bucket}/moved/move_me.txt", str(dest))
    assert down.returncode == 0
    assert dest.read_text() == "payload-to-move"


def test_rm_single_key_removes_only_that_key(cli, bucket, tmp_path, s3_client):
    _require_s3_client(s3_client)
    for key in ("keep/one.txt", "keep/two.txt"):
        f = tmp_path / "f.txt"
        f.write_text("x")
        assert cli("s3", "cp", str(f), f"s3://{bucket}/{key}").returncode == 0

    result = cli("s3", "rm", f"s3://{bucket}/keep/one.txt")
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""
    assert SUCCESS_LINE_RE.search(result.stdout)

    remaining = s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])
    keys = {o["Key"] for o in remaining}
    assert "keep/one.txt" not in keys
    assert "keep/two.txt" in keys


def test_rm_recursive_removes_only_prefix(cli, bucket, tmp_path, s3_client):
    _require_s3_client(s3_client)
    for key in ("prefix/a.txt", "prefix/sub/b.txt", "other/c.txt"):
        f = tmp_path / "f.txt"
        f.write_text("x")
        assert cli("s3", "cp", str(f), f"s3://{bucket}/{key}").returncode == 0

    result = cli("s3", "rm", f"s3://{bucket}/prefix/", "--recursive")
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""

    remaining = s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])
    keys = {o["Key"] for o in remaining}
    assert "prefix/a.txt" not in keys
    assert "prefix/sub/b.txt" not in keys
    assert "other/c.txt" in keys


def test_sync_local_to_s3_then_noop_second_run(cli, bucket, tmp_path, s3_client):
    _require_s3_client(s3_client)
    src_dir = tmp_path / "syncsrc"
    src_dir.mkdir()
    (src_dir / "one.txt").write_text("one")
    (src_dir / "two.txt").write_text("two")

    first = cli("s3", "sync", str(src_dir), f"s3://{bucket}/synced/")
    assert first.returncode == 0, first.stderr
    assert first.stderr == ""

    listed = s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])
    keys = {o["Key"] for o in listed}
    assert "synced/one.txt" in keys
    assert "synced/two.txt" in keys

    second = cli("s3", "sync", str(src_dir), f"s3://{bucket}/synced/")
    assert second.returncode == 0, second.stderr
    assert second.stderr == ""
    # no-op run: no transfer lines like "upload:" should appear
    assert "upload:" not in second.stdout.lower()


def test_cp_nonexistent_bucket_fails_cleanly(cli, tmp_path):
    src = tmp_path / "f.txt"
    src.write_text("x")
    missing_bucket = _bucket_name()

    result = cli("s3", "cp", str(src), f"s3://{missing_bucket}/f.txt")

    assert result.returncode in ALLOWED_EXIT_CODES
    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr.strip() != ""


def test_missing_required_args_exit_nonzero_no_stdout(cli):
    result = cli("s3", "cp")

    assert result.returncode in ALLOWED_EXIT_CODES
    assert result.returncode != 0
    assert result.stdout == ""
    assert result.stderr.strip() != ""


def test_rm_forwards_request_payer_without_error(cli, bucket, tmp_path):
    f = tmp_path / "payer.txt"
    f.write_text("payer-data")
    up = cli("s3", "cp", str(f), f"s3://{bucket}/payer/payer.txt")
    assert up.returncode == 0, up.stderr

    result = cli(
        "s3", "rm", f"s3://{bucket}/payer/payer.txt", "--request-payer", "requester"
    )
    # should either succeed cleanly or fail with a classed error, never a
    # stack trace or stdout-on-failure violation
    if result.returncode == 0:
        assert result.stderr == ""
        assert SUCCESS_LINE_RE.search(result.stdout)
    else:
        assert result.returncode in ALLOWED_EXIT_CODES
        assert result.stdout == ""
        assert result.stderr.strip() != ""