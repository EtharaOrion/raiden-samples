


def test_workflow_sync_then_ls_then_cp(cli, s3_client, tmp_path):
    bucket = "test-sync-ls-cp-bucket"
    s3_client.create_bucket(Bucket=bucket)

    srcdir = tmp_path / "src"
    srcdir.mkdir()
    files = {
        "a.txt": b"alpha-content",
        "b.txt": b"beta-content",
        "sub/c.txt": b"gamma-content",
    }
    for rel, data in files.items():
        p = srcdir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    r = cli("s3", "sync", str(srcdir), f"s3://{bucket}")
    assert r.returncode == 0

    resp = s3_client.list_objects_v2(Bucket=bucket)
    keys = {o["Key"] for o in resp.get("Contents", [])}
    expected_keys = {"a.txt", "b.txt", "sub/c.txt"}
    assert expected_keys.issubset(keys)

    for rel, data in files.items():
        got = s3_client.get_object(Bucket=bucket, Key=rel)["Body"].read()
        assert got == data

    r = cli("s3", "ls", f"s3://{bucket}/")
    assert r.returncode == 0

    r = cli("s3", "ls", "s3://definitely-no-such-bucket-xyz-987654")
    assert r.returncode != 0
    out = tmp_path / "fetched_a.txt"
    r = cli("s3", "cp", f"s3://{bucket}/a.txt", str(out))
    assert r.returncode == 0
    assert out.read_bytes() == files["a.txt"]

    r = cli("s3", "rb", f"s3://{bucket}", "--force")
    assert r.returncode == 0
    buckets = {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
    assert bucket not in buckets
