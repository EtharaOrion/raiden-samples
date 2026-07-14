import uuid

from _s3_http import S3HTTPError as ClientError


def test_rm_followed_by_head_object_returns_404(cli, s3_client):
    bucket = f"b-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="target.bin", Body=b"removable")

    head_before = s3_client.head_object(Bucket=bucket, Key="target.bin")
    assert head_before["ContentLength"] == len(b"removable")

    result = cli("s3", "rm", f"s3://{bucket}/target.bin")
    assert result.returncode == 0, result.stderr

    try:
        s3_client.head_object(Bucket=bucket, Key="target.bin")
        raise AssertionError("head_object should return 404 after rm")
    except ClientError as e:
        assert e.response["Error"]["Code"] in ("404", "NoSuchKey")
