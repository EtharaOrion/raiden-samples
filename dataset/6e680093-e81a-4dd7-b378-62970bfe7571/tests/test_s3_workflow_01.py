from _s3_http import S3HTTPError as ClientError


import uuid


def test_workflow_sync_mv_state(cli, s3_client, tmp_path):
    bucket = f"test-sync-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)

    srcdir = tmp_path / "src"
    srcdir.mkdir()
    files = {
        "a.txt": b"alpha",
        "b.txt": b"beta",
        "sub/c.txt": b"charlie",
    }
    for rel, data in files.items():
        p = srcdir / rel
        p.parent.mkdir(parents=True, exist_ok=True)
        p.write_bytes(data)

    r = cli("s3", "sync", str(srcdir), f"s3://{bucket}")
    assert r.returncode == 0

    listed = s3_client.list_objects_v2(Bucket=bucket).get("Contents", [])
    keys = {o["Key"] for o in listed}
    expected = {"a.txt", "b.txt", "sub/c.txt"}
    assert expected.issubset(keys)
    assert s3_client.get_object(Bucket=bucket, Key="a.txt")["Body"].read() == b"alpha"

    r = cli("s3", "mv", f"s3://{bucket}/a.txt", f"s3://{bucket}/moved/a.txt")
    assert r.returncode == 0

    try:
        s3_client.head_object(Bucket=bucket, Key="a.txt")
        raise AssertionError("a.txt should be moved away")
    except ClientError as e:
        assert e.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound")

    assert s3_client.get_object(Bucket=bucket, Key="moved/a.txt")["Body"].read() == b"alpha"

    r = cli("s3", "ls", f"s3://{bucket}")
    assert r.returncode == 0
