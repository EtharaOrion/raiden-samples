

def test_workflow_mb_cp_rm_lifecycle(cli, s3_client, tmp_path):
    import uuid
    from _s3_http import S3HTTPError as ClientError

    bucket = f"test-lifecycle-{uuid.uuid4().hex[:12]}"
    src = tmp_path / "hello.txt"
    payload = b"hello world\n\x00\x01binary"
    src.write_bytes(payload)

    r = cli("s3", "mb", f"s3://{bucket}")
    assert r.returncode == 0
    assert bucket in {b["Name"] for b in s3_client.list_buckets()["Buckets"]}

    r = cli("s3", "cp", str(src), f"s3://{bucket}/hello.txt")
    assert r.returncode == 0
    got = s3_client.get_object(Bucket=bucket, Key="hello.txt")["Body"].read()
    assert got == payload

    dst = tmp_path / "hello-rt.txt"
    r = cli("s3", "cp", f"s3://{bucket}/hello.txt", str(dst))
    assert r.returncode == 0
    assert dst.read_bytes() == payload

    r = cli("s3", "rm", f"s3://{bucket}/hello.txt")
    assert r.returncode == 0
    try:
        s3_client.head_object(Bucket=bucket, Key="hello.txt")
        raise AssertionError("object should be gone")
    except ClientError as e:
        assert e.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound")

    r = cli("s3", "rb", f"s3://{bucket}")
    assert r.returncode == 0
    assert bucket not in {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
