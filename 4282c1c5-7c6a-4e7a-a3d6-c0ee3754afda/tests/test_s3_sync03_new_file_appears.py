import uuid


def test_sync03_new_file_appears(cli, s3_client, tmp_path):
    """Sync, add new local file, sync again -> new file appears in S3."""
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    (tmp_path / "a.txt").write_bytes(b"first")
    r1 = cli("s3", "sync", str(tmp_path), f"s3://{bucket}/p")
    assert r1.returncode == 0, r1.stderr
    (tmp_path / "b.txt").write_bytes(b"second")
    r2 = cli("s3", "sync", str(tmp_path), f"s3://{bucket}/p")
    assert r2.returncode == 0, r2.stderr
    keys = {o["Key"] for o in s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])}
    assert "p/a.txt" in keys, f"missing a.txt; got {keys}"
    assert "p/b.txt" in keys, f"missing b.txt; got {keys}"
