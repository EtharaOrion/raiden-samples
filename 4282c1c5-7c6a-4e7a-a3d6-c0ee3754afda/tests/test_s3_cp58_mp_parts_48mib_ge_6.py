import uuid


def test_cp58_mp_parts_48mib_ge_6(cli, s3_client, tmp_path):
    """48 MiB upload must yield ETag with >= 6 parts."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    src = tmp_path / "big.bin"
    src.write_bytes(b'R' * 50331648)
    r = cli("s3", "cp", str(src), f"s3://{bucket}/big.bin")
    assert r.returncode == 0, r.stderr
    head = s3_client.head_object(Bucket=bucket, Key="big.bin")
    etag = head["ETag"].strip('"')
    assert "-" in etag, f"expected multipart ETag, got {etag!r}"
    parts = int(etag.split("-")[-1])
    assert parts >= 6, f"expected >= 6 parts, got {parts} (etag={etag})"
