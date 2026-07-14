import uuid


def test_cp07_missing_local_src_fails_with_path_in_stderr(cli, s3_client, tmp_path):
    """Missing local source must fail and name the missing file in stderr."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    missing = tmp_path / "nope_cp07.bin"
    r = cli("s3", "cp", str(missing), f"s3://{bucket}/k")
    assert r.returncode in (1, 255), (
        f"expected returncode in (1,255), got {r.returncode}; stderr={r.stderr!r}"
    )
    assert (
        "nope_cp07.bin" in r.stderr or str(missing) in r.stderr
    ), f"missing path should be referenced in stderr: {r.stderr!r}"
    assert "Traceback (most recent call last)" not in r.stderr
