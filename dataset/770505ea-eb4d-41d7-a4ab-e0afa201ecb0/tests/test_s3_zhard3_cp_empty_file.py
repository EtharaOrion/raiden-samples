import uuid


def test_zhard3_cp_empty_file_uploads_zero_byte_object(cli, s3_client, tmp_path):
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    src = tmp_path / "empty.txt"
    src.write_bytes(b"")
    r = cli("s3", "cp", str(src), f"s3://{bucket}/empty")
    assert r.returncode == 0, r.stderr
    head = s3_client.head_object(Bucket=bucket, Key="empty")
    assert head["ContentLength"] == 0, f"expected 0 bytes, got {head['ContentLength']}"
