import uuid

from _s3_http import S3HTTPError as ClientError


def test_rm_then_head_object_returns_404(cli, s3_client):
    bucket = f"b-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="goodbye.txt", Body=b"gone-soon")

    result = cli("s3", "rm", f"s3://{bucket}/goodbye.txt")
    assert result.returncode == 0, result.stderr

    try:
        s3_client.head_object(Bucket=bucket, Key="goodbye.txt")
        raise AssertionError("object should be deleted")
    except ClientError as e:
        assert e.response["Error"]["Code"] in ("404", "NoSuchKey")
