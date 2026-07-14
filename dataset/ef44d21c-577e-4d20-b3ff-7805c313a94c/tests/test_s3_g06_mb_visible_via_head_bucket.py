import uuid


def test_mb_makes_bucket_visible_via_head_bucket(cli, s3_client):
    bucket = f"b-{uuid.uuid4().hex[:12]}"

    result = cli("s3", "mb", f"s3://{bucket}")
    assert result.returncode == 0, result.stderr

    head = s3_client.head_bucket(Bucket=bucket)
    assert head["ResponseMetadata"]["HTTPStatusCode"] == 200
