import uuid


def test_zhard4_sync_preserves_deep_directory_structure(cli, s3_client, tmp_path):
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    src = tmp_path / "src"
    (src / "a" / "b" / "c").mkdir(parents=True)
    (src / "a" / "b" / "c" / "deep.txt").write_bytes(b"deep")
    (src / "a" / "shallow.txt").write_bytes(b"shallow")
    (src / "top.txt").write_bytes(b"top")
    r = cli("s3", "sync", str(src), f"s3://{bucket}/p")
    assert r.returncode == 0, r.stderr
    keys = {o["Key"] for o in s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])}
    assert "p/top.txt" in keys, f"missing p/top.txt in {keys}"
    assert "p/a/shallow.txt" in keys, f"missing p/a/shallow.txt in {keys}"
    assert "p/a/b/c/deep.txt" in keys, f"missing p/a/b/c/deep.txt in {keys}"
