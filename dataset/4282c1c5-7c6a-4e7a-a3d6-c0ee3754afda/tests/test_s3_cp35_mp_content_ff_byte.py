import uuid


def test_cp35_mp_content_ff_byte(cli, s3_client, tmp_path):
    """10 MiB upload with varied content must produce multipart ETag."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    src = tmp_path / "content.bin"
    src.write_bytes(b'\xff' * (10 * 1024 * 1024))
    r = cli("s3", "cp", str(src), f"s3://{bucket}/content.bin")
    assert r.returncode == 0, r.stderr
    head = s3_client.head_object(Bucket=bucket, Key="content.bin")
    etag = head["ETag"].strip('"')
    assert "-" in etag, f"expected multipart ETag, got {etag!r}"
