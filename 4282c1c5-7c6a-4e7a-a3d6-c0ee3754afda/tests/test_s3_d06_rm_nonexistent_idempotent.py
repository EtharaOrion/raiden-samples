import uuid


def test_rm_nonexistent_object_exits_zero(cli, s3_client):
    bucket = f"b-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="keep.txt", Body=b"k")

    result = cli("s3", "rm", f"s3://{bucket}/nothing-here.txt")
    assert result.returncode == 0, result.stderr

    assert s3_client.get_object(Bucket=bucket, Key="keep.txt")["Body"].read() == b"k"
