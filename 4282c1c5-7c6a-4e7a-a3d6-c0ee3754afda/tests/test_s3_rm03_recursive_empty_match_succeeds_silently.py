import uuid


def test_rm03_recursive_empty_match_succeeds_silently(cli, s3_client, tmp_path):
    """rm --recursive matching zero keys -> exit 0, empty stderr."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="other", Body=b"x")
    r = cli("s3", "rm", f"s3://{bucket}/never", "--recursive")
    assert r.returncode == 0, f"got {r.returncode}; stderr={r.stderr!r}"
    assert r.stderr == "", f"expected empty stderr, got: {r.stderr!r}"
