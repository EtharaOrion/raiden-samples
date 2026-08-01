import hashlib
import uuid


def test_zhard2_cp_sha256_upload_download_roundtrip(cli, s3_client, tmp_path):
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    src = tmp_path / "src.bin"
    data = b"".join([b"abc" * 100, bytes(range(256)), b"\x00" * 500, b"\xff" * 500])
    src.write_bytes(data)
    src_sha = hashlib.sha256(data).hexdigest()
    r1 = cli("s3", "cp", str(src), f"s3://{bucket}/k")
    assert r1.returncode == 0, r1.stderr
    dst = tmp_path / "dst.bin"
    r2 = cli("s3", "cp", f"s3://{bucket}/k", str(dst))
    assert r2.returncode == 0, r2.stderr
    dst_sha = hashlib.sha256(dst.read_bytes()).hexdigest()
    assert dst_sha == src_sha, "sha256 mismatch after upload/download roundtrip"
