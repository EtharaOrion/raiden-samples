import uuid


def test_ls_recursive_line_count_matches_object_count(cli, s3_client):
    bucket = f"b-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    keys = [f"k-{i:03d}.txt" for i in range(5)]
    for k in keys:
        s3_client.put_object(Bucket=bucket, Key=k, Body=b"x")

    result = cli("s3", "ls", f"s3://{bucket}/", "--recursive")
    assert result.returncode == 0, result.stderr

    matched = [k for k in keys if k in result.stdout]
    assert matched == keys
