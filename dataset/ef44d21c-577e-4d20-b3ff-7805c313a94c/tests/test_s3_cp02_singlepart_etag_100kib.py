import uuid


def test_cp02_singlepart_etag_100kib(cli, s3_client, tmp_path):
    """100 KiB upload must be single-part (ETag has NO dash)."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    src = tmp_path / "small.bin"
    src.write_bytes(b"S" * (100 * 1024))
    result = cli("s3", "cp", str(src), f"s3://{bucket}/small.bin")
    assert result.returncode == 0, result.stderr
    head = s3_client.head_object(Bucket=bucket, Key="small.bin")
    etag = head["ETag"].strip('"')
    assert "-" not in etag, f"expected single-part ETag for 100KiB, got {etag!r}"
