import uuid


def test_cp03_bytes_roundtrip_all_values(cli, s3_client, tmp_path):
    """Byte-identical roundtrip of bytes(range(256))."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    payload = bytes(range(256))
    src = tmp_path / "bin.bin"
    src.write_bytes(payload)
    dst = tmp_path / "out.bin"
    r1 = cli("s3", "cp", str(src), f"s3://{bucket}/bin.bin")
    assert r1.returncode == 0, r1.stderr
    r2 = cli("s3", "cp", f"s3://{bucket}/bin.bin", str(dst))
    assert r2.returncode == 0, r2.stderr
    assert dst.read_bytes() == payload, "byte mismatch after roundtrip"
