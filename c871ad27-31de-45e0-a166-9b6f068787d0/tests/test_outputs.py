"""Held-out frozen tests generated from the task behavioral contract by
raiden verifier (model: claude-sonnet-5). Supplementary overfit probe — run with the
shipped tests/conftest.py in the task environment. NOT executed by the
process verifier (the task runtime image is not available to it)."""

import pytest

"""Held-out tests for the `aws` s3-subset CLI emulator.

These tests exercise cross-command state consistency, output-contract
shape, and exit-code behavior against a real MinIO backend, using the
`cli` and `s3_client` fixtures provided by the shipped conftest.py.
"""

import os
import time
import uuid

import pytest

ACCEPTED_ERROR_CODES = {1, 2, 252, 255}


def _uniq_bucket(prefix="held-out"):
    return f"{prefix}-{uuid.uuid4().hex[:12]}"


def test_cp_local_to_s3_to_local_roundtrip_byte_identical(cli, s3_client, tmp_path):
    bucket = _uniq_bucket()
    s3_client.create_bucket(Bucket=bucket)

    content = os.urandom(4096)
    src = tmp_path / "payload.bin"
    src.write_bytes(content)

    up = cli("s3", "cp", str(src), f"s3://{bucket}/payload.bin")
    assert up.returncode == 0, up.stderr
    assert up.stderr == ""
    assert up.stdout.strip() != ""

    # cross-command consistency: the object must really exist server-side
    obj = s3_client.get_object(Bucket=bucket, Key="payload.bin")
    assert obj["Body"].read() == content

    dest = tmp_path / "roundtrip.bin"
    down = cli("s3", "cp", f"s3://{bucket}/payload.bin", str(dest))
    assert down.returncode == 0, down.stderr
    assert down.stderr == ""
    assert dest.read_bytes() == content


def test_ls_empty_bucket_success_no_output(cli, s3_client):
    bucket = _uniq_bucket()
    s3_client.create_bucket(Bucket=bucket)

    result = cli("s3", "ls", f"s3://{bucket}")
    assert result.returncode == 0
    assert result.stdout.strip() == ""
    assert result.stderr == ""


def test_ls_nonexistent_bucket_fails_cleanly(cli):
    bucket = _uniq_bucket("nope")
    result = cli("s3", "ls", f"s3://{bucket}")
    assert result.returncode != 0
    assert result.returncode in ACCEPTED_ERROR_CODES
    assert result.stdout == ""
    assert result.stderr.strip() != ""
    assert "traceback" not in result.stderr.lower()


def test_ls_recursive_flattens_no_pre_lines(cli, s3_client):
    bucket = _uniq_bucket()
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="dir1/a.txt", Body=b"a")
    s3_client.put_object(Bucket=bucket, Key="dir2/b.txt", Body=b"b")

    result = cli("s3", "ls", f"s3://{bucket}", "--recursive")
    assert result.returncode == 0
    assert result.stderr == ""
    assert "PRE" not in result.stdout
    assert "dir1/a.txt" in result.stdout
    assert "dir2/b.txt" in result.stdout


def test_mv_deletes_source_after_successful_copy(cli, s3_client, tmp_path):
    bucket = _uniq_bucket()
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="src.txt", Body=b"hello world")

    result = cli("s3", "mv", f"s3://{bucket}/src.txt", f"s3://{bucket}/dst.txt")
    assert result.returncode == 0, result.stderr
    assert result.stderr == ""

    keys = {o["Key"] for o in s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])}
    assert "dst.txt" in keys
    assert "src.txt" not in keys


def test_mv_self_move_fails_without_side_effects(cli, s3_client):
    bucket = _uniq_bucket()
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="same.txt", Body=b"data")

    result = cli("s3", "mv", f"s3://{bucket}/same.txt", f"s3://{bucket}/same.txt")
    assert result.returncode != 0
    assert result.returncode in ACCEPTED_ERROR_CODES
    assert result.stdout == ""

    # object must remain untouched
    obj = s3_client.get_object(Bucket=bucket, Key="same.txt")
    assert obj["Body"].read() == b"data"


def test_rb_nonempty_requires_force_then_succeeds(cli, s3_client):
    bucket = _uniq_bucket()
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="a.txt", Body=b"x")

    no_force = cli("s3", "rb", f"s3://{bucket}")
    assert no_force.returncode != 0
    assert no_force.stdout == ""

    bucket_names = {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
    assert bucket in bucket_names

    forced = cli("s3", "rb", f"s3://{bucket}", "--force")
    assert forced.returncode == 0, forced.stderr
    assert forced.stderr == ""

    bucket_names_after = {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
    assert bucket not in bucket_names_after


def test_sync_local_to_s3_idempotent_on_repeat(cli, s3_client, tmp_path):
    bucket = _uniq_bucket()
    s3_client.create_bucket(Bucket=bucket)

    src_dir = tmp_path / "srcdir"
    src_dir.mkdir()
    (src_dir / "f1.txt").write_text("one")
    (src_dir / "f2.txt").write_text("two")

    first = cli("s3", "sync", str(src_dir), f"s3://{bucket}")
    assert first.returncode == 0, first.stderr
    assert first.stderr == ""

    keys = {o["Key"] for o in s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])}
    assert {"f1.txt", "f2.txt"}.issubset(keys)

    second = cli("s3", "sync", str(src_dir), f"s3://{bucket}")
    assert second.returncode == 0, second.stderr
    assert second.stderr == ""
    # idempotent: nothing new should have been transferred
    lower = second.stdout.lower()
    assert "f1.txt" not in lower
    assert "f2.txt" not in lower


def test_sync_missing_local_source_fails(cli):
    bucket = _uniq_bucket()
    missing_dir = f"/tmp/does-not-exist-{uuid.uuid4().hex}"
    result = cli("s3", "sync", missing_dir, f"s3://{bucket}")
    assert result.returncode != 0
    assert result.returncode in ACCEPTED_ERROR_CODES
    assert result.stdout == ""
    assert result.stderr.strip() != ""


def test_unknown_flag_rejected_with_usage_error(cli, s3_client):
    bucket = _uniq_bucket()
    s3_client.create_bucket(Bucket=bucket)

    result = cli("s3", "ls", f"s3://{bucket}", "--totally-bogus-flag")
    assert result.returncode != 0
    assert result.returncode in ACCEPTED_ERROR_CODES
    assert result.stdout == ""
    assert result.stderr.strip() != ""


def test_mv_missing_required_args_fails(cli):
    result = cli("s3", "mv")
    assert result.returncode != 0
    assert result.returncode in ACCEPTED_ERROR_CODES
    assert result.stdout == ""


def test_cp_sse_kms_persisted_and_observable(cli, s3_client, tmp_path):
    bucket = _uniq_bucket()
    s3_client.create_bucket(Bucket=bucket)

    src = tmp_path / "secret.txt"
    src.write_text("top secret content")

    result = cli(
        "s3", "cp", str(src), f"s3://{bucket}/secret.txt",
        "--sse", "aws:kms",
        "--sse-kms-key-id", "arbitrary-test-key",
    )
    # If the backend/KMS setup rejects the key, this must still fail
    # cleanly (not with a traceback); if it succeeds, encryption metadata
    # must be observable on the stored object.
    if result.returncode == 0:
        assert result.stderr == ""
        head = s3_client.head_object(Bucket=bucket, Key="secret.txt")
        headers_blob = str(head).lower()
        assert "kms" in headers_blob or "aws:kms" in headers_blob or "encrypt" in headers_blob
    else:
        assert result.returncode in ACCEPTED_ERROR_CODES
        assert result.stdout == ""