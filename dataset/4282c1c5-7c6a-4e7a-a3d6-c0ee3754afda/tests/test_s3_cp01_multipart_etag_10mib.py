import uuid


def test_cp01_multipart_etag_10mib(cli, s3_client, tmp_path):
    """10 MiB upload must use multipart (ETag contains a dash)."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    src = tmp_path / "big.bin"
    src.write_bytes(b"A" * (10 * 1024 * 1024))
    result = cli("s3", "cp", str(src), f"s3://{bucket}/big.bin")
    assert result.returncode == 0, result.stderr
    head = s3_client.head_object(Bucket=bucket, Key="big.bin")
    etag = head["ETag"].strip('"')
    assert "-" in etag, f"expected multipart ETag (dash suffix), got {etag!r}"
