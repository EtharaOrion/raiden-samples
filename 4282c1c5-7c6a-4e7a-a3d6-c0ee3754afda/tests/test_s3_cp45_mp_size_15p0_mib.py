import uuid


def test_cp45_mp_size_15p0_mib(cli, s3_client, tmp_path):
    """Upload >8 MiB (15.0 MiB) must produce multipart ETag (dash suffix)."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    src = tmp_path / "big.bin"
    src.write_bytes(b'K' * 15728640)
    r = cli("s3", "cp", str(src), f"s3://{bucket}/big.bin")
    assert r.returncode == 0, r.stderr
    head = s3_client.head_object(Bucket=bucket, Key="big.bin")
    etag = head["ETag"].strip('"')
    assert "-" in etag, f"expected multipart ETag for 15.0 MiB upload, got {etag!r}"
