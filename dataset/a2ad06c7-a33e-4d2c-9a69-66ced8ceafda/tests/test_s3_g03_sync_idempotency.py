import hashlib
import uuid


def test_sync_idempotent_preserves_state(cli, s3_client, tmp_path):
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)

    src_dir = tmp_path / "src"
    src_dir.mkdir()
    payload = b"sync-idempotent-payload-XYZ"
    (src_dir / "f.bin").write_bytes(payload)

    r1 = cli("s3", "sync", str(src_dir), f"s3://{bucket}/k")
    assert r1.returncode == 0, r1.stderr
    body1 = s3_client.get_object(Bucket=bucket, Key="k/f.bin")["Body"].read()
    assert body1 == payload

    r2 = cli("s3", "sync", str(src_dir), f"s3://{bucket}/k")
    assert r2.returncode == 0, r2.stderr
    body2 = s3_client.get_object(Bucket=bucket, Key="k/f.bin")["Body"].read()

    assert hashlib.sha256(body1).hexdigest() == hashlib.sha256(body2).hexdigest()
    keys = {o["Key"] for o in s3_client.list_objects_v2(Bucket=bucket).get("Contents", []) or []}
    assert keys == {"k/f.bin"}
