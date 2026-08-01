import uuid


def test_sync04_delete_local_without_flag_keeps_s3_object(cli, s3_client, tmp_path):
    """Sync, delete local file, plain sync (NO --delete) -> S3 object survives."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    (tmp_path / "a.txt").write_bytes(b"keep-me")
    (tmp_path / "b.txt").write_bytes(b"orphan")
    r1 = cli("s3", "sync", str(tmp_path), f"s3://{bucket}/p")
    assert r1.returncode == 0, r1.stderr
    (tmp_path / "b.txt").unlink()
    r2 = cli("s3", "sync", str(tmp_path), f"s3://{bucket}/p")
    assert r2.returncode == 0, r2.stderr
    keys = {o["Key"] for o in s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])}
    assert "p/b.txt" in keys, f"orphan should survive plain sync; got {keys}"
