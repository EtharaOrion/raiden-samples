import uuid


def test_u02_no_traceback_on_error(cli, s3_client, tmp_path):
    """Error path: no raw traceback in stderr; the offending path must appear."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    missing = tmp_path / "does_not_exist_u02.bin"
    result = cli("s3", "cp", str(missing), f"s3://{bucket}/k")
    assert result.returncode != 0, (
        f"expected nonzero exit, got 0; stdout={result.stdout!r}"
    )
    assert "Traceback (most recent call last)" not in result.stderr, (
        f"raw traceback leaked to stderr: {result.stderr!r}"
    )
    assert "does_not_exist_u02.bin" in result.stderr or str(missing) in result.stderr, (
        f"missing path should be referenced in stderr: {result.stderr!r}"
    )
