import uuid


def test_u03_success_stderr_empty(cli, s3_client, tmp_path):
    """Stream segregation: successful op writes nothing to stderr."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    src = tmp_path / "hi.txt"
    src.write_bytes(b"hi")
    result = cli("s3", "cp", str(src), f"s3://{bucket}/hi.txt")
    assert result.returncode == 0, result.stderr
    assert result.stderr == "", (
        f"expected empty stderr on success, got: {result.stderr!r}"
    )
