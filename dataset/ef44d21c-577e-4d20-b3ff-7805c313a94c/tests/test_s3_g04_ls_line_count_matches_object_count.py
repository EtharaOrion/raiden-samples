import uuid


def test_ls_recursive_line_count_matches_object_count(cli, s3_client):
    bucket = f"b-{uuid.uuid4().hex[:12]}"
    s3_client.create_bucket(Bucket=bucket)
    keys = [f"prefix/k{i:02d}.txt" for i in range(6)]
    for k in keys:
        s3_client.put_object(Bucket=bucket, Key=k, Body=k.encode())

    result = cli("s3", "ls", f"s3://{bucket}/", "--recursive")
    assert result.returncode == 0, result.stderr

    matched = sum(1 for line in result.stdout.splitlines() if any(k in line for k in keys))
    assert matched == len(keys)
