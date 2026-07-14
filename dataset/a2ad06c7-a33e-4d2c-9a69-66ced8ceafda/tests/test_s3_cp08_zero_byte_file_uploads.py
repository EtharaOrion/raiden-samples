import uuid


def test_cp08_zero_byte_file_uploads(cli, s3_client, tmp_path):
    """0-byte file uploads successfully with ContentLength==0."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    src = tmp_path / "empty"
    src.write_bytes(b"")
    r = cli("s3", "cp", str(src), f"s3://{bucket}/empty")
    assert r.returncode == 0, r.stderr
    head = s3_client.head_object(Bucket=bucket, Key="empty")
    assert head["ContentLength"] == 0
