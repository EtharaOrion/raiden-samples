import uuid


def test_mv_self_move_fails_with_nonzero_exit(cli, s3_client):
    bucket = f"b-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    s3_client.put_object(Bucket=bucket, Key="same.txt", Body=b"untouched")

    r0 = cli("s3", "ls")
    assert r0.returncode == 0, r0.stderr
    assert bucket in r0.stdout

    result = cli("s3", "mv", f"s3://{bucket}/same.txt", f"s3://{bucket}/same.txt")
    assert result.returncode != 0

    body = s3_client.get_object(Bucket=bucket, Key="same.txt")["Body"].read()
    assert body == b"untouched"
