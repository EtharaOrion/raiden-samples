from _s3_http import S3HTTPError as ClientError


import os
import uuid


def test_workflow_mb_cp_roundtrip_rm(cli, s3_client, tmp_path):
    bucket = f"test-bucket-{uuid.uuid4().hex[:12]}"
    key = "data/hello.bin"

    result = cli("s3", "mb", f"s3://{bucket}")
    assert result.returncode == 0

    buckets = {b["Name"] for b in s3_client.list_buckets()["Buckets"]}
    assert bucket in buckets

    src = tmp_path / "hello.bin"
    payload = os.urandom(2048)
    src.write_bytes(payload)

    result = cli("s3", "cp", str(src), f"s3://{bucket}/{key}")
    assert result.returncode == 0

    got = s3_client.get_object(Bucket=bucket, Key=key)["Body"].read()
    assert got == payload

    dst = tmp_path / "hello_roundtrip.bin"
    result = cli("s3", "cp", f"s3://{bucket}/{key}", str(dst))
    assert result.returncode == 0
    assert dst.read_bytes() == payload

    result = cli("s3", "rm", f"s3://{bucket}/{key}")
    assert result.returncode == 0

    try:
        s3_client.head_object(Bucket=bucket, Key=key)
        raise AssertionError("object should be deleted")
    except ClientError as e:
        assert e.response["Error"]["Code"] in ("404", "NoSuchKey", "NotFound")

    result = cli("s3", "rm", f"s3://{bucket}/{key}")
    assert result.returncode == 0
