"""Argv-grammar and operation-vocabulary tests.

These tests grade the additions documented in ``instruction.md``'s
"Operation vocabulary" subsection and "Flag inventory" section: every
documented success verb, every documented transfer flag, and the
spec-mandated failure *class* (AWS error code or generic failure phrase)
the harness checks.
"""

import uuid

import pytest

from conftest import _stderr_names_error


def _no_traceback(stream: str) -> bool:
    return "Traceback (most recent call last)" not in stream


def _first_nonempty_line(s: str) -> str:
    return next((line for line in s.splitlines() if line.strip()), "")


def _bucket() -> str:
    return f"grammar-{uuid.uuid4().hex[:12]}"


def test_verb_mb_make_bucket(cli, s3_client):
    bucket = _bucket()
    r = cli("s3", "mb", f"s3://{bucket}")
    assert r.returncode == 0, r.stderr
    assert _first_nonempty_line(r.stdout).startswith("make_bucket:"), (
        f"mb stdout must begin with 'make_bucket:'; got {r.stdout!r}"
    )


def test_verb_rb_remove_bucket(cli, s3_client):
    bucket = _bucket()
    s3_client.create_bucket(Bucket=bucket)
    r = cli("s3", "rb", f"s3://{bucket}")
    assert r.returncode == 0, r.stderr
    assert _first_nonempty_line(r.stdout).startswith("remove_bucket:"), (
        f"rb stdout must begin with 'remove_bucket:'; got {r.stdout!r}"
    )


def test_verb_rb_force_emits_delete_per_object(cli, s3_client):
    bucket = _bucket()
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="a.txt", Body=b"x")
    r = cli("s3", "rb", f"s3://{bucket}", "--force")
    assert r.returncode == 0, r.stderr
    delete_lines = [ln for ln in r.stdout.splitlines() if ln.startswith("delete:")]
    assert delete_lines, (
        f"rb --force must emit at least one 'delete:' line; got {r.stdout!r}"
    )


def test_verb_cp_upload(cli, s3_client, tmp_path):
    bucket = _bucket()
    s3_client.create_bucket(Bucket=bucket)
    src = tmp_path / "f.bin"
    src.write_bytes(b"verb-cp-upload")
    r = cli("s3", "cp", str(src), f"s3://{bucket}/f.bin")
    assert r.returncode == 0, r.stderr
    assert any(ln.startswith("upload:") for ln in r.stdout.splitlines()), (
        f"cp local->s3 stdout must contain an 'upload:' line; got {r.stdout!r}"
    )


def test_verb_cp_download(cli, s3_client, tmp_path):
    bucket = _bucket()
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="f.bin", Body=b"verb-cp-dl")
    dst = tmp_path / "out.bin"
    r = cli("s3", "cp", f"s3://{bucket}/f.bin", str(dst))
    assert r.returncode == 0, r.stderr
    assert any(ln.startswith("download:") for ln in r.stdout.splitlines()), (
        f"cp s3->local stdout must contain a 'download:' line; got {r.stdout!r}"
    )


def test_verb_cp_copy_s3_to_s3(cli, s3_client):
    bucket = _bucket()
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="a.bin", Body=b"verb-cp-copy")
    r = cli("s3", "cp", f"s3://{bucket}/a.bin", f"s3://{bucket}/b.bin")
    assert r.returncode == 0, r.stderr
    assert any(ln.startswith("copy:") for ln in r.stdout.splitlines()), (
        f"cp s3->s3 stdout must contain a 'copy:' line; got {r.stdout!r}"
    )


def test_verb_mv_move(cli, s3_client):
    bucket = _bucket()
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="src.bin", Body=b"verb-mv")
    r = cli("s3", "mv", f"s3://{bucket}/src.bin", f"s3://{bucket}/dst.bin")
    assert r.returncode == 0, r.stderr
    assert any(ln.startswith("move:") for ln in r.stdout.splitlines()), (
        f"mv stdout must contain a 'move:' line; got {r.stdout!r}"
    )


def test_verb_sync_upload(cli, s3_client, tmp_path):
    bucket = _bucket()
    s3_client.create_bucket(Bucket=bucket)
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "x.bin").write_bytes(b"verb-sync")
    r = cli("s3", "sync", str(src_dir), f"s3://{bucket}/")
    assert r.returncode == 0, r.stderr
    upload_lines = [ln for ln in r.stdout.splitlines() if ln.startswith("upload:")]
    assert upload_lines, (
        f"sync local->s3 must emit at least one 'upload:' line; got {r.stdout!r}"
    )


@pytest.mark.parametrize("flag,value", [
    ("--sse", "aws:kms"),
    ("--sse-kms-key-id", "arn:aws:kms:us-east-1:000000000000:key/abc"),
    ("--metadata-directive", "COPY"),
    ("--storage-class", "STANDARD"),
    ("--content-type", "text/plain"),
    ("--cache-control", "no-store"),
    ("--acl", "private"),
])
def test_flag_cp_accepts_value_flag(cli, s3_client, tmp_path, flag, value):
    bucket = _bucket()
    s3_client.create_bucket(Bucket=bucket)
    src = tmp_path / "f.bin"
    src.write_bytes(b"flag-accept")
    r = cli("s3", "cp", str(src), f"s3://{bucket}/f.bin", flag, value)
    assert r.returncode != 255, (
        f"cp must accept documented flag {flag}; got returncode {r.returncode} "
        f"with stderr {r.stderr!r}"
    )
    assert _no_traceback(r.stderr)


@pytest.mark.parametrize("flag", ["--quiet", "--dryrun", "--only-show-errors"])
def test_flag_cp_accepts_boolean_flag(cli, s3_client, tmp_path, flag):
    bucket = _bucket()
    s3_client.create_bucket(Bucket=bucket)
    src = tmp_path / "f.bin"
    src.write_bytes(b"bool-flag")
    r = cli("s3", "cp", str(src), f"s3://{bucket}/f.bin", flag)
    assert r.returncode != 255, (
        f"cp must accept documented boolean flag {flag}; got returncode "
        f"{r.returncode} with stderr {r.stderr!r}"
    )
    assert _no_traceback(r.stderr)


@pytest.mark.parametrize("flag,value", [
    ("--exclude", "*.tmp"),
    ("--include", "*.bin"),
])
def test_flag_sync_accepts_repeatable_flag(cli, s3_client, tmp_path, flag, value):
    bucket = _bucket()
    s3_client.create_bucket(Bucket=bucket)
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "ok.bin").write_bytes(b"x")
    r = cli("s3", "sync", str(src_dir), f"s3://{bucket}/", flag, value)
    assert r.returncode != 255, (
        f"sync must accept documented flag {flag}; got returncode "
        f"{r.returncode} with stderr {r.stderr!r}"
    )
    assert _no_traceback(r.stderr)


def test_flag_sync_rejects_recursive(cli, s3_client, tmp_path):
    bucket = _bucket()
    s3_client.create_bucket(Bucket=bucket)
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "x.bin").write_bytes(b"x")
    r = cli("s3", "sync", str(src_dir), f"s3://{bucket}/", "--recursive")
    assert r.returncode in (2, 252, 255), (
        f"sync must reject --recursive as unknown; got returncode {r.returncode}"
    )
    lower = r.stderr.lower()
    assert "--recursive" in r.stderr or "unknown" in lower, (
        f"sync --recursive rejection must explain the unknown option; got {r.stderr!r}"
    )
    assert _no_traceback(r.stderr)


def test_wording_rb_failed_phrase(cli):
    r = cli("s3", "rb", f"s3://{_bucket()}")
    assert r.returncode != 0
    assert _stderr_names_error(r.stderr), (
        f"rb on non-existent bucket must surface an error class/phrase in "
        f"stderr; got {r.stderr!r}"
    )
    assert _no_traceback(r.stderr)


def test_wording_mv_self_move_phrase(cli, s3_client):
    bucket = _bucket()
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="x.bin", Body=b"x")
    uri = f"s3://{bucket}/x.bin"
    r = cli("s3", "mv", uri, uri)
    assert r.returncode != 0
    assert _stderr_names_error(r.stderr) or "itself" in r.stderr.lower(), (
        f"mv self-move must surface error class or contain 'itself'; got {r.stderr!r}"
    )
    assert _no_traceback(r.stderr)
