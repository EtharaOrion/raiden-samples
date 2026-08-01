import uuid


def test_rm04_missing_single_key_idempotent(cli, s3_client, tmp_path):
    """rm s3://b/never-existed-key (no --recursive) -> exit 0, empty stderr."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    r = cli("s3", "rm", f"s3://{bucket}/never-existed-key")
    assert r.returncode == 0, f"got {r.returncode}; stderr={r.stderr!r}"
    assert r.stderr == "", f"expected empty stderr, got: {r.stderr!r}"
