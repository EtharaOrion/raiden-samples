import uuid


def test_ls_page_size_does_not_truncate_results(cli, s3_client):
    bucket = f"b-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    keys = [f"k{i:02d}.txt" for i in range(7)]
    for k in keys:
        s3_client.put_object(Bucket=bucket, Key=k, Body=b"x")

    result = cli("s3", "ls", f"s3://{bucket}/", "--page-size", "2")
    assert result.returncode == 0, result.stderr
    for k in keys:
        assert k in result.stdout
