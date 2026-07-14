"""Output-contract tests for the documented stdout shape, stderr error
class, exit-code policy, and traceback hygiene.

These tests do not introduce new behavior; they make the contract that
``instruction.md`` documents in its "Output contract" section explicit and
graded, so that a model trained from spec has a path to learn the UX
surface the harness checks.
"""

import re
import shutil
import uuid

import pytest


@pytest.fixture(autouse=True)
def _require_submission():
    """Anti-NOP guard local to the contract tests.

    Refuses to pass any contract test unless an ``aws`` executable is on
    ``$PATH`` (the agent's own submission, written in any language and
    installed at any location on ``$PATH``). Mirrors the guard in
    ``conftest.py``. Without this, the checks could trivially pass on a
    NOP run, defeating discrimination.
    """
    if shutil.which("aws") is None:
        pytest.fail(
            "Anti-NOP guard: no `aws` executable on $PATH; "
            "contract tests cannot pass without a real submission."
        )


ALLOWED_ERROR_CODES = (
    "NoSuchBucket",
    "NoSuchKey",
    "BucketAlreadyExists",
    "BucketAlreadyOwnedByYou",
    "InvalidBucketName",
    "BucketNotEmpty",
    "AccessDenied",
    "InvalidRequest",
    "InvalidArgument",
    "InvalidS3URI",
)
_STDOUT_SHAPE = re.compile(r"^[a-z_]+:\s+\S")

def _no_traceback(stream: str) -> bool:
    return "Traceback (most recent call last)" not in stream

def _first_nonempty_line(s: str) -> str:
    return next((line for line in s.splitlines() if line.strip()), "")

_FAILURE_PHRASES = (
    " failed",
    "does not exist",
    "no such",
    "not found",
    "an error occurred",
    "cannot",
    "invalid",
    "unable",
    "could not",
    "must be",
    "is required",
    "usage",
    "unknown",
    "parameter validation",
    "are required",
    "unrecognized",
)

def _stderr_names_error(stderr: str) -> bool:
    lower = stderr.lower()
    if any(code.lower() in lower for code in ALLOWED_ERROR_CODES):
        return True
    return any(p in lower for p in _FAILURE_PHRASES)

def _bucket() -> str:
    return f"contract-{uuid.uuid4().hex[:12]}"

def test_contract_stdout_shape_mb(cli, s3_client):
    bucket = _bucket()
    r = cli("s3", "mb", f"s3://{bucket}")
    assert r.returncode == 0, f"mb happy path must succeed; stderr={r.stderr!r}"
    assert bucket in {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
    line = _first_nonempty_line(r.stdout)
    assert _STDOUT_SHAPE.match(line), (
        f"mb success stdout must match '<operation>: <resource>'; got {line!r}"
    )
    assert _no_traceback(r.stderr)

def test_contract_unknown_flag_mb(cli):
    r = cli("s3", "mb", f"s3://{_bucket()}", "--no-such-flag-x9q")
    assert r.returncode != 0, (
        f"unknown flag on mb must fail with non-zero exit; got {r.returncode}"
    )
    assert _no_traceback(r.stderr)

def test_contract_missing_arg_mb(cli):
    r = cli("s3", "mb")
    assert r.returncode != 0, (
        f"missing required arg on mb must fail with non-zero exit; got {r.returncode}"
    )
    assert r.stderr.strip()
    assert _no_traceback(r.stderr)

def test_contract_stderr_error_class_mb(cli):
    r = cli("s3", "mb", "s3://ab")
    assert r.returncode != 0, "mb on invalid bucket must fail"
    assert _stderr_names_error(r.stderr), (
        f"mb error must surface an AWS error code or 'X failed'; got {r.stderr!r}"
    )
    assert _no_traceback(r.stderr)

def test_contract_stdout_shape_cp(cli, s3_client, tmp_path):
    bucket = _bucket()
    s3_client.create_bucket(Bucket=bucket)
    src = tmp_path / "payload.txt"
    src.write_bytes(b"contract-cp-stdout")
    r = cli("s3", "cp", str(src), f"s3://{bucket}/payload.txt")
    assert r.returncode == 0, f"cp happy path must succeed; stderr={r.stderr!r}"
    obj = s3_client.get_object(Bucket=bucket, Key="payload.txt")
    assert obj["Body"].read() == b"contract-cp-stdout"
    assert any(
        _STDOUT_SHAPE.match(ln) for ln in r.stdout.splitlines() if ln.strip()
    ), (
        f"cp success stdout must contain a '<operation>: <resource>' line; "
        f"got {r.stdout!r}"
    )
    assert _no_traceback(r.stderr)

def test_contract_unknown_flag_cp(cli, tmp_path):
    src = tmp_path / "f.txt"
    src.write_bytes(b"x")
    r = cli("s3", "cp", str(src), f"s3://{_bucket()}/k", "--no-such-flag-x9q")
    assert r.returncode != 0
    assert _no_traceback(r.stderr)

def test_contract_missing_arg_cp(cli):
    r = cli("s3", "cp")
    assert r.returncode != 0
    assert r.stderr.strip()
    assert _no_traceback(r.stderr)

def test_contract_stderr_error_class_cp(cli, tmp_path):
    src = tmp_path / "f.txt"
    src.write_bytes(b"x")
    r = cli("s3", "cp", str(src), f"s3://{_bucket()}/k")
    assert r.returncode != 0
    assert _stderr_names_error(r.stderr), (
        f"cp error must surface error class or 'X failed'; got {r.stderr!r}"
    )
    assert _no_traceback(r.stderr)

def test_contract_stdout_shape_mv(cli, s3_client, tmp_path):
    bucket = _bucket()
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="src.txt", Body=b"mv-contract")
    r = cli("s3", "mv", f"s3://{bucket}/src.txt", f"s3://{bucket}/dst.txt")
    assert r.returncode == 0, f"mv happy path must succeed; stderr={r.stderr!r}"
    assert s3_client.get_object(Bucket=bucket, Key="dst.txt")["Body"].read() == b"mv-contract"
    with pytest.raises(s3_client.exceptions.ClientError):
        s3_client.head_object(Bucket=bucket, Key="src.txt")
    assert any(
        _STDOUT_SHAPE.match(ln) for ln in r.stdout.splitlines() if ln.strip()
    ), (
        f"mv success stdout must contain a '<operation>: <resource>' line; "
        f"got {r.stdout!r}"
    )
    assert _no_traceback(r.stderr)

def test_contract_unknown_flag_mv(cli):
    src = f"s3://{_bucket()}/a"
    dst = f"s3://{_bucket()}/b"
    r = cli("s3", "mv", src, dst, "--no-such-flag-x9q")
    assert r.returncode != 0
    assert _no_traceback(r.stderr)

def test_contract_missing_arg_mv(cli):
    r = cli("s3", "mv")
    assert r.returncode != 0
    assert r.stderr.strip()
    assert _no_traceback(r.stderr)

def test_contract_stderr_error_class_mv(cli, s3_client):
    bucket = _bucket()
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="x.txt", Body=b"x")
    r = cli("s3", "mv", f"s3://{bucket}/x.txt", f"s3://{bucket}/x.txt")
    assert r.returncode != 0
    assert _stderr_names_error(r.stderr) or "itself" in r.stderr.lower(), (
        f"mv self-move error must surface error class, 'X failed', or "
        f"'itself'; got {r.stderr!r}"
    )
    assert _no_traceback(r.stderr)

def test_contract_stdout_shape_sync(cli, s3_client, tmp_path):
    bucket = _bucket()
    s3_client.create_bucket(Bucket=bucket)
    src_dir = tmp_path / "src"
    src_dir.mkdir()
    (src_dir / "a.txt").write_bytes(b"sync-contract")
    r = cli("s3", "sync", str(src_dir), f"s3://{bucket}/")
    assert r.returncode == 0, f"sync happy path must succeed; stderr={r.stderr!r}"
    assert s3_client.get_object(Bucket=bucket, Key="a.txt")["Body"].read() == b"sync-contract"
    assert any(
        _STDOUT_SHAPE.match(ln) for ln in r.stdout.splitlines() if ln.strip()
    ), (
        f"sync success stdout must contain a '<operation>: <resource>' line; "
        f"got {r.stdout!r}"
    )
    assert _no_traceback(r.stderr)

def test_contract_unknown_flag_sync(cli, tmp_path):
    (tmp_path / "src").mkdir()
    r = cli(
        "s3", "sync", str(tmp_path / "src"), f"s3://{_bucket()}/",
        "--no-such-flag-x9q",
    )
    assert r.returncode != 0
    assert _no_traceback(r.stderr)

def test_contract_missing_arg_sync(cli):
    r = cli("s3", "sync")
    assert r.returncode != 0
    assert r.stderr.strip()
    assert _no_traceback(r.stderr)

def test_contract_stderr_error_class_sync(cli, tmp_path):
    missing = tmp_path / "does-not-exist"
    r = cli("s3", "sync", str(missing), f"s3://{_bucket()}/")
    assert r.returncode != 0
    assert _stderr_names_error(r.stderr) or "does not exist" in r.stderr.lower(), (
        f"sync error must surface error class, 'X failed', or 'does not "
        f"exist'; got {r.stderr!r}"
    )
    assert _no_traceback(r.stderr)

def test_contract_unknown_flag_ls(cli):
    r = cli("s3", "ls", "--no-such-flag-x9q")
    assert r.returncode != 0, (
        f"unknown flag on ls must fail with non-zero exit; got {r.returncode}"
    )
    assert _no_traceback(r.stderr)

def test_contract_stderr_error_class_ls(cli):
    r = cli("s3", "ls", f"s3://{_bucket()}")
    assert r.returncode != 0, "ls on non-existent bucket must fail"
    assert _stderr_names_error(r.stderr), (
        f"ls error must surface error class or 'X failed'; got {r.stderr!r}"
    )
    assert _no_traceback(r.stderr)
