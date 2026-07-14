import hashlib
import uuid


def test_cp_roundtrip_sha256_matches(cli, s3_client, tmp_path):
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)

    src = tmp_path / "src.bin"
    payload = bytes(range(256)) * 8
    src.write_bytes(payload)
    src_hash = hashlib.sha256(payload).hexdigest()

    r = cli("s3", "cp", str(src), f"s3://{bucket}/k.bin")
    assert r.returncode == 0, r.stderr

    dst = tmp_path / "dst.bin"
    r = cli("s3", "cp", f"s3://{bucket}/k.bin", str(dst))
    assert r.returncode == 0, r.stderr

    assert hashlib.sha256(dst.read_bytes()).hexdigest() == src_hash
