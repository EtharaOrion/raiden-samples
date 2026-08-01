import uuid


def test_cp04_utf8_bom_multibyte_roundtrip(cli, s3_client, tmp_path):
    """UTF-8 BOM + multibyte payload roundtrips byte-identical."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    payload = b"\xef\xbb\xbf" + "h\u00e9llo\U0001f30d".encode("utf-8")
    src = tmp_path / "utf8.txt"
    src.write_bytes(payload)
    dst = tmp_path / "out.txt"
    r1 = cli("s3", "cp", str(src), f"s3://{bucket}/utf8.txt")
    assert r1.returncode == 0, r1.stderr
    r2 = cli("s3", "cp", f"s3://{bucket}/utf8.txt", str(dst))
    assert r2.returncode == 0, r2.stderr
    assert dst.read_bytes() == payload, "byte mismatch in UTF-8 roundtrip"
