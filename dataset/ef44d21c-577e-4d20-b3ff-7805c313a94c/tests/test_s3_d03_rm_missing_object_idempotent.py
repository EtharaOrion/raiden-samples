import uuid


def test_rm_missing_object_succeeds_silently(cli, s3_client):
    bucket = f"b-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="bystander.txt", Body=b"keep")

    result = cli("s3", "rm", f"s3://{bucket}/no-such-key.txt")
    assert result.returncode == 0, result.stderr

    body = s3_client.get_object(Bucket=bucket, Key="bystander.txt")["Body"].read()
    assert body == b"keep"
