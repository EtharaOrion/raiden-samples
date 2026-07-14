from _s3_http import S3HTTPError as ClientError


def test_workflow_mb_sync_rm_rb_lifecycle(cli, s3_client, tmp_path):

    bucket = "test-lifecycle-bucket-xyz123"
    src = tmp_path / "src"
    src.mkdir()
    (src / "a.txt").write_bytes(b"hello-a")
    (src / "b.txt").write_bytes(b"hello-b")
    sub = src / "sub"
    sub.mkdir()
    (sub / "c.txt").write_bytes(b"hello-c")

    r = cli("s3", "mb", f"s3://{bucket}")
    assert r.returncode == 0
    buckets = {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
    assert bucket in buckets

    r = cli("s3", "sync", str(src), f"s3://{bucket}")
    assert r.returncode == 0

    resp = s3_client.list_objects_v2(Bucket=bucket)
    keys = {o["Key"] for o in resp.get("Contents", [])}
    assert {"a.txt", "b.txt", "sub/c.txt"}.issubset(keys)

    assert s3_client.get_object(Bucket=bucket, Key="a.txt")["Body"].read() == b"hello-a"
    assert s3_client.get_object(Bucket=bucket, Key="sub/c.txt")["Body"].read() == b"hello-c"

    r = cli("s3", "rm", f"s3://{bucket}/a.txt")
    assert r.returncode == 0
    try:
        s3_client.head_object(Bucket=bucket, Key="a.txt")
        raise AssertionError("a.txt should be gone")
    except ClientError as e:
        assert e.response["Error"]["Code"] in ("404", "NoSuchKey", "NoSuchBucket")

    r = cli("s3", "rb", f"s3://{bucket}", "--force")
    assert r.returncode == 0
    buckets = {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
    assert bucket not in buckets
