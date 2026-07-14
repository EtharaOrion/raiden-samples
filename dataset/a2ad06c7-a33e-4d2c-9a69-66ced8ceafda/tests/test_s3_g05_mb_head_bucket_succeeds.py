import uuid


def test_mb_head_bucket_succeeds_after_create(cli, s3_client):
    bucket = f"test-{uuid.uuid4().hex[:12]}"
    result = cli("s3", "mb", f"s3://{bucket}")
    assert result.returncode == 0, result.stderr

    s3_client.head_bucket(Bucket=bucket)
