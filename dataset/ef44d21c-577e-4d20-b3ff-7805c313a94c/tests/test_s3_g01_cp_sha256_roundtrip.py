import hashlib
import os
import uuid


def test_cp_roundtrip_sha256_byte_equality(cli, s3_client, tmp_path):
    bucket = f"b-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)

    src = tmp_path / "src.bin"
    payload = os.urandom(16 * 1024)
    src.write_bytes(payload)
    original_sha = hashlib.sha256(payload).hexdigest()

    r1 = cli("s3", "cp", str(src), f"s3://{bucket}/obj.bin")
    assert r1.returncode == 0, r1.stderr

    dst = tmp_path / "out.bin"
    r2 = cli("s3", "cp", f"s3://{bucket}/obj.bin", str(dst))
    assert r2.returncode == 0, r2.stderr

    downloaded = dst.read_bytes()
    assert hashlib.sha256(downloaded).hexdigest() == original_sha
    assert downloaded == payload
