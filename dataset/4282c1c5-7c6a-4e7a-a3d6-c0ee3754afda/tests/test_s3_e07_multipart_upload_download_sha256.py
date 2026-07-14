import hashlib
import uuid


def test_e07_multipart_upload_download_sha256(cli, s3_client, tmp_path):
    """10 MiB multipart upload + download roundtrip: sha256 unchanged."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    payload = (bytes(range(256)) * ((10 * 1024 * 1024 // 256) + 1))[: 10 * 1024 * 1024]
    src = tmp_path / "big.bin"
    src.write_bytes(payload)
    expected_sha = hashlib.sha256(payload).hexdigest()
    r1 = cli("s3", "cp", str(src), f"s3://{bucket}/big.bin")
    assert r1.returncode == 0, r1.stderr
    dst = tmp_path / "out.bin"
    r2 = cli("s3", "cp", f"s3://{bucket}/big.bin", str(dst))
    assert r2.returncode == 0, r2.stderr
    actual_sha = hashlib.sha256(dst.read_bytes()).hexdigest()
    assert actual_sha == expected_sha, "sha256 differs after multipart roundtrip"
