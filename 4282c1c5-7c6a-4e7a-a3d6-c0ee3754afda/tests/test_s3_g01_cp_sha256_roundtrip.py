import hashlib
import os
import uuid


def test_cp_sha256_roundtrip_matches(cli, s3_client, tmp_path):
    bucket = f"b-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)

    src = tmp_path / "src.bin"
    payload = os.urandom(32 * 1024)
    src.write_bytes(payload)
    src_sha = hashlib.sha256(payload).hexdigest()

    r_up = cli("s3", "cp", str(src), f"s3://{bucket}/round.bin")
    assert r_up.returncode == 0, r_up.stderr

    out = tmp_path / "out.bin"
    r_dn = cli("s3", "cp", f"s3://{bucket}/round.bin", str(out))
    assert r_dn.returncode == 0, r_dn.stderr

    out_sha = hashlib.sha256(out.read_bytes()).hexdigest()
    assert out_sha == src_sha
