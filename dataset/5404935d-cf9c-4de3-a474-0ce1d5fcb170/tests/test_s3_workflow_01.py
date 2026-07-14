

def test_workflow_sync_then_rb_force(cli, s3_client, tmp_path):
    import uuid

    bucket = f"test-sync-rb-{uuid.uuid4().hex[:12]}"
    r = cli("s3", "mb", f"s3://{bucket}")
    assert r.returncode == 0

    srcdir = tmp_path / "src"
    srcdir.mkdir()
    files = {"a.txt": b"AAAA", "b.txt": b"BBBB", "sub/c.txt": b"CCCC"}
    for rel, data in files.items():
        p = srcdir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    r = cli("s3", "sync", str(srcdir), f"s3://{bucket}/")
    assert r.returncode == 0

    listed = s3_client.list_objects_v2(Bucket=bucket).get("Contents", []) or []
    keys = {o["Key"] for o in listed}
    expected = {"a.txt", "b.txt", "sub/c.txt"}
    assert expected.issubset(keys)
    for rel, data in files.items():
        assert s3_client.get_object(Bucket=bucket, Key=rel)["Body"].read() == data

    r = cli("s3", "rb", f"s3://{bucket}")
    assert r.returncode != 0
    assert bucket in {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
    still = s3_client.list_objects_v2(Bucket=bucket).get("Contents", []) or []
    assert {o["Key"] for o in still}.issuperset(expected)

    r = cli("s3", "rb", f"s3://{bucket}", "--force")
    assert r.returncode == 0
    assert bucket not in {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
