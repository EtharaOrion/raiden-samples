from _s3_http import S3HTTPError as ClientError


import uuid


def test_workflow_mb_cp_roundtrip_rm_rb(cli, s3_client, tmp_path):
    bucket = f"test-rt-{uuid.uuid4().hex[:12]}"
    key = "hello.txt"
    payload = b"hello world\n\x00\x01binary"

    src = tmp_path / "src.txt"
    src.write_bytes(payload)
    dst = tmp_path / "dst.txt"

    r = cli("s3", "mb", f"s3://{bucket}")
    assert r.returncode == 0
    buckets = {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
    assert bucket in buckets

    r = cli("s3", "cp", str(src), f"s3://{bucket}/{key}")
    assert r.returncode == 0
    got = s3_client.get_object(Bucket=bucket, Key=key)["Body"].read()
    assert got == payload

    r = cli("s3", "cp", f"s3://{bucket}/{key}", str(dst))
    assert r.returncode == 0
    assert dst.read_bytes() == payload

    r = cli("s3", "rm", f"s3://{bucket}/{key}")
    assert r.returncode == 0
    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        raise AssertionError("object should be gone")
    except ClientError as e:
        assert e.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound")

    r = cli("s3", "rb", f"s3://{bucket}")
    assert r.returncode == 0
    buckets = {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
    assert bucket not in buckets
